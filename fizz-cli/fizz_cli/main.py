import time
import typer

from click import clear
from rich import print

from .utils import (
    bold_blue,
    check_fission_directory,
    delete_file_if_exists,
    ensure_leading_slash,
    enumerate_functions,
    get_fn_route_path,
    read_yaml_file,
    rename_fn_in_specs,
    rename_folder,
    replace_route,
    save_yaml_file,
    update_shell_scripts,
)

app = typer.Typer()
route_app = typer.Typer(help=f"Manage {bold_blue('routes')} for functions.")
fn_app = typer.Typer(
    help=f"Manage {bold_blue('functions')}. fn is not mandatory, all commands pertaining to functions also work without fn keyword ."
)

app.add_typer(route_app, name="route")
app.add_typer(fn_app, name="fn")


@app.command()
@fn_app.command()
def new(function_name: str):
    """
    Creates a new function with the given name.
    """
    print(f"Creating new function: {function_name} \n")


@app.command()
@fn_app.command()
def rename(function_name: str, new_name: str):
    """
    Renames an existing function to a new name.
    """
    typer.confirm(
        "Modify folder name? NOTE: bash/bat scripts will also be modified.",
        default=True,
        abort=True,
    )
    new_fn_name = typer.prompt(
        "New function name: ", default="", show_default=False, fg=typer.colors.YELLOW
    )
    success = rename_folder(function_name, new_fn_name)

    if success:
        print("[:white_check_mark:][block green]Folder renamed.[/block green]")
    else:
        print(
            "[:heavy_exclamation_mark:][block red] Folder name not found for the exact function name.\n"
            "[:heavy_exclamation_mark:] Default folder naming convention is not being used.[/block red]"
        )

    success = update_shell_scripts(function_name, new_fn_name)
    if success:
        print(f"[block green]sh/bat scripts updated[/block green]")
    else:
        print(
            f":heavy_exclamation_mark:[block red]failed to update sh/bat scripts[/block red]"
        )

    rename_fn_in_specs(function_name, new_fn_name)
    print(f"[block green]Function renaming in specs done.[/block green]")


@route_app.command("rename")
def route_rename(function_name: str, new_route_name: str):
    """
    Renames a route associated with a function to a new route name.
    """
    _, data = read_yaml_file("route", function_name)
    data = replace_route(data, new_route_name)
    save_yaml_file("route", function_name, data)

    print(
        f"[bold green]Created or renamed {function_name} route to {ensure_leading_slash(new_route_name)}[/bold green]"
    )


@route_app.command("delete")
def route_delete(function_name: str):
    """
    Deletes the route of the function.
    """
    path = get_fn_route_path(function_name)
    if path is not None:
        delete_file_if_exists(path)
    else:
        print(
            f"[bold red]Couldn't find route-{function_name}.yaml in the specs directory or the proper "
            f"naming conventions hasn't been used.[/bold red]"
        )


@app.command()
@app.command()
def i():
    exit_cli = False
    while exit_cli is False:
        clear()
        print("[🧰] What would you like to do?")
        print("1. Modify Existing Function")
        print("2. Create New Function")
        print("3. Initialise Fission")

        choice = typer.prompt("Enter the number corresponding to your choice:")

        if choice == 1:
            exists = check_fission_directory()

            if exists:
                func_list = enumerate_functions()
                function_name = typer.prompt(
                    f"Existing Functions: {func_list}\nChoose a function to modify:",
                    type=str,
                )

                print(
                    f"[:hammer_and_wrench:] [bold green]{function_name}[/bold green] [bold blue]Modification Options:[/bold blue]"
                )
                print("1. Rename Route")
                print("2. Delete Route")
                print("3. Rename Function")
                print("4. Delete Function")

                idx = typer.prompt(
                    "Select an option:",
                    type=int,
                )

                if idx == 1:
                    new_route = typer.prompt(
                        "Enter the new route name:",
                        default="",
                        show_default=False,
                        fg=typer.colors.YELLOW,
                    )
                    route_rename(function_name, new_route)

                elif idx == 2:
                    route_delete(function_name)

                elif idx == 3:
                    pass  # Add your logic here for renaming the function

                elif idx == 4:
                    pass  # Add your logic here for deleting the function

            else:
                print(
                    ":boom: [bold red]Incorrect Directory![/bold red] [yellow]Navigate to the level where "
                    "the specs folder exists.[/yellow]"
                )
        else:
            typer.echo("New")

        time.sleep(2)

