import subprocess
import time

import typer
from click import clear
from rich import print

from .utils import bold_blue
from .utils import check_fission_directory
from .utils import create_new_fn_spec_and_boilerplate
from .utils import delete_file_if_exists
from .utils import delete_function
from .utils import ensure_leading_slash
from .utils import enumerate_functions
from .utils import exec_package_script
from .utils import get_fn_route_path
from .utils import id_generator
from .utils import init_fission
from .utils import read_yaml_file
from .utils import rename_fn_in_specs
from .utils import rename_folder
from .utils import replace_route
from .utils import save_yaml_file
from .utils import update_shell_scripts
from .utils import get_current_environment

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
    created = create_new_fn_spec_and_boilerplate(function_name)
    env = get_current_environment()
    if created:
        executed = exec_package_script()
        if executed:
            subprocess.run(
                f'fission package create --sourcearchive {function_name}.zip --env {env} --buildcmd "./build.sh"  --name {function_name} --spec',
                shell=True,
                text=False,
                capture_output=False,
            )
            subprocess.run(
                f'fission fn create --name {function_name} --pkg {function_name} --entrypoint "main.main" --env=ipl-2024 --spec',
                shell=True,
                text=False,
                capture_output=False,
            )
            subprocess.run(
                f"fission route create --name {function_name} --method GET --method POST --url /{function_name} --function {function_name} --spec",
                shell=True,
                text=False,
                capture_output=False,
            )


@app.command()
def init():
    """
    Initialise fission in the current directory so that fission development can be started
    """
    print(
        "[bold green]:white_heavy_check_mark:Fission Spec Initialisation Completed.[/bold green]"
    )
    init_fission()


@app.command()
@fn_app.command()
def delete(function_name: str):
    """
    Deletes the code folder and the function, route and package specs.
    """
    deleted = delete_function(function_name)
    if deleted:
        print(
            f"[bold green]Function '{function_name}' deleted successfully.[/bold green]"
        )
    else:
        print(f"[bold red]Failed to delete function '{function_name}'.[/bold red]")


@app.command()
@fn_app.command()
def rename(fn_name: str):
    """
    Renames an existing function to a new name.
    """
    typer.confirm(
        "Modify folder name? NOTE: bash/bat scripts will also be modified.",
        default=True,
        abort=True,
    )
    new_fn_name = typer.prompt(
        "Function Name: ",
        default=bold_blue(f"function{id_generator()}"),
    )
    success = rename_folder(fn_name, new_fn_name)

    if success:
        print("[bold green][:white_check_mark:]Folder renamed.[/bold green]")
    else:
        print(
            "[bold red]"
            "[:heavy_exclamation_mark:] Folder name not found for the exact function name.\n"
            "[:heavy_exclamation_mark:] Default folder naming convention is not being used."
            "[/bold red]"
        )

    success = update_shell_scripts(fn_name, new_fn_name)
    if success:
        print(f"[bold green]sh/bat scripts updated[/bold green]")
    else:
        print(
            f":heavy_exclamation_mark:[bold red]failed to update sh/bat scripts[/bold red]"
        )

    rename_fn_in_specs(fn_name, new_fn_name)
    print(f"[bold green]Function renaming in specs done.[/bold green]")


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
def i():
    """
    Interactive Mode
    """
    exit_cli = False
    while exit_cli is False:
        clear()
        print(
            "[:toolbox:] What would you like to do? \n"
            "[:wrench:]\t1) Modify Existing Function \n"
            "[:new:]\t2) Create New Function \n"
            "[:green_square:]\t0) Initialise Fission"
        )
        choice = typer.prompt("Choice", type=int)

        if choice == 1:
            exists = check_fission_directory()
            if not exists:
                print(
                    "[bold red]"
                    ":boom::skull: Incorrect Directory!"
                    "[/bold red] "
                    "[yellow]"
                    "Navigate to the level where the specs folder exists."
                    "[/yellow]"
                )
                time.sleep(2)
                continue

            func_list = enumerate_functions()
            fn_name = typer.prompt(
                f"Existing Functions: {func_list}\nChoose a function to modify:",
                type=str,
            )

            print(
                f"[bold green][:hammer_and_wrench:] {fn_name}[/bold green] "
                f"[bold blue]Modification Options:[/bold blue]"
            )

            print(
                "[:toolbox:] What would you like to do? \n"
                ":pencil:\t1) Rename Route\n"
                ":skull:\t2) Delete Route\n"
                ":spiral_notepad:\t3) Rename Function\n"
                ":cross_mark:\t4) Delete Function"
            )
            choice = typer.prompt("Choice", type=int)

            if choice == 1:
                new_route = typer.prompt(
                    bold_blue("Enter the new route name"),
                    show_default=False,
                )
                route_rename(fn_name, new_route)

            elif choice == 2:
                route_delete(fn_name)
            elif choice == 3:
                rename(fn_name)
            elif choice == 4:
                delete(fn_name)
        elif choice == 2:
            folder_name = typer.prompt("Enter the new function name")
            new(folder_name)
        elif choice == 0:
            init()
        else:
            typer.echo("Invalid Choice!")
            time.sleep(1)
            continue

        time.sleep(5)
