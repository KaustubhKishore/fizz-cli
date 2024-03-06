# Fizz CLI

```
 ________  __                     
|        \|  \                    
| $$$$$$$$ \$$ ________  ________ 
| $$__    |  \|        \|        \
| $$  \   | $$ \$$$$$$$$ \$$$$$$$$
| $$$$$   | $$  /    $$   /    $$ 
| $$      | $$ /  $$$$_  /  $$$$_ 
| $$      | $$|  $$    \|  $$    \
 \$$       \$$ \$$$$$$$$ \$$$$$$$$
                                  
```                                  
                                  

Fission CLI wrapper for easy project management. 

## Usage
```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `delete`: Deletes the code folder and the function,...
* `fn`: Manage functions.
* `i`: Interactive Mode
* `init`: Initialise fission in the current...
* `new`: Creates a new function with the given name.
* `rename`: Renames an existing function to a new name.
* `route`: Manage routes for functions.

## `delete`

Deletes the code folder and the function, route and package specs.

**Usage**:

```console
$ delete [OPTIONS] FUNCTION_NAME
```

**Arguments**:

* `FUNCTION_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `fn`

Manage functions. fn is not mandatory, all commands pertaining to functions also work without fn keyword .

**Usage**:

```console
$ fn [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `delete`: Deletes the code folder and the function,...
* `new`: Creates a new function with the given name.
* `rename`: Renames an existing function to a new name.

### `fn delete`

Deletes the code folder and the function, route and package specs.

**Usage**:

```console
$ fn delete [OPTIONS] FUNCTION_NAME
```

**Arguments**:

* `FUNCTION_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

### `fn new`

Creates a new function with the given name.

**Usage**:

```console
$ fn new [OPTIONS] FUNCTION_NAME
```

**Arguments**:

* `FUNCTION_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

### `fn rename`

Renames an existing function to a new name.

**Usage**:

```console
$ fn rename [OPTIONS] FN_NAME
```

**Arguments**:

* `FN_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `i`

Interactive Mode

**Usage**:

```console
$ i [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `init`

Initialise fission in the current directory so that fission development can be started

**Usage**:

```console
$ init [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `new`

Creates a new function with the given name.

**Usage**:

```console
$ new [OPTIONS] FUNCTION_NAME
```

**Arguments**:

* `FUNCTION_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `rename`

Renames an existing function to a new name.

**Usage**:

```console
$ rename [OPTIONS] FN_NAME
```

**Arguments**:

* `FN_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `route`

Manage routes for functions.

**Usage**:

```console
$ route [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `delete`: Deletes the route of the function.
* `rename`: Renames a route associated with a function...

### `route delete`

Deletes the route of the function.

**Usage**:

```console
$ route delete [OPTIONS] FUNCTION_NAME
```

**Arguments**:

* `FUNCTION_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

### `route rename`

Renames a route associated with a function to a new route name.

**Usage**:

```console
$ route rename [OPTIONS] FUNCTION_NAME NEW_ROUTE_NAME
```

**Arguments**:

* `FUNCTION_NAME`: [required]
* `NEW_ROUTE_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.
