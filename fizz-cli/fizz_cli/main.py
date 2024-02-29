import time

import typer
from bullet import Bullet
from bullet import Input
from bullet import YesNo
from bullet import colors
from click import clear
from rich import print

from .utils import bold_blue
from .utils import check_fission_directory
from .utils import delete_file_if_exists
from .utils import ensure_leading_slash
from .utils import enumerate_functions
from .utils import get_fn_route_path
from .utils import read_yaml_file
from .utils import rename_folder
from .utils import replace_route
from .utils import save_yaml_file
from .utils import styled_bullet
from .utils import update_shell_scripts
from .utils import rename_fn_in_specs

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
    print(f"Renaming {function_name} to {new_name}")


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
    exit_cli = False
    while exit_cli is False:
        clear()
        new_or_existing = styled_bullet(
            "[🧰] What would you like to do?",
            [
                "Modify Existing Function",
                "Create New Function",
                "Initialise Fission",
            ],
        )

        _, idx = new_or_existing.launch()

        if idx == 0:
            exists = check_fission_directory()

            if exists:
                func_list = enumerate_functions()
                modify_existing: Bullet = styled_bullet(
                    "Existing Functions: ", func_list
                )
                function_name, _ = modify_existing.launch()

                print(
                    f"[:hammer_and_wrench:] [bold green]{function_name}[/bold green] [bold blue]Modification Options:[/bold blue]"
                )
                modification_options = styled_bullet(
                    "",
                    [
                        "Rename Route",
                        "Delete Route",
                        "Rename Function",
                        "Delete Function",
                    ],
                )

                _, idx = modification_options.launch()
                if idx == 0:
                    new_route = Input(
                        "New route name: ",
                        default="",
                        word_color=colors.foreground["yellow"],
                    )

                    res = new_route.launch()
                    route_rename(function_name, res)
                elif idx == 1:
                    route_delete(function_name)
                elif idx == 2:
                    folder_mod = YesNo(
                        "Modify folder name? NOTE: bash/bat scripts will also be modified.",
                        default="y",
                    )

                    folder_mod = folder_mod.launch()
                    if folder_mod:
                        new_fn_name = Input(
                            "New function name: ",
                            default="",
                            word_color=colors.foreground["yellow"],
                        )
                        new_fn_name = new_fn_name.launch()
                        success = rename_folder(function_name, new_fn_name)

                        if success:
                            print(
                                "[:white_check_mark:][block green]Folder renamed.[/block green]"
                            )
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
                        print(
                            f"[block green]Function renaming in specs done.[/block green]"
                        )
            else:
                print(
                    ":boom: [bold red]Incorrect Directory![/bold red] [yellow]Navigate to the level where "
                    "the specs folder exists.[/yellow]"
                )
        else:
            typer.echo("New")

        time.sleep(2)
