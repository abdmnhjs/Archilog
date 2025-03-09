import click
import uuid
from typing import Optional
from flask import Flask, render_template, request, flash, redirect, url_for
import archilog.models as models
import archilog.services as services

app = Flask(__name__)

@app.route("/archilog/")
@app.route("/archilog/menu")
def menu():
    return render_template('archilog.html')

@app.route("/archilog/create", methods=['GET', 'POST'])
def createInWebSite():
    if request.method == 'POST':
        nom = request.form.get('nom')
        categorie = request.form.get('categorie', 'Aucune catégorie')
        prix = request.form.get('prix')

        prix = float(prix)
        create.callback(name=nom, amount=prix, category=categorie)
        return redirect(url_for("getUpdateDeleteInWebSite"))

    return render_template("create.html")

@app.route("/archilog/getUpdateDelete", methods=['GET', 'POST'])
def getUpdateDeleteInWebSite():
    searched = None
    message = None
    data = models.get_all_entries()
    entries = [[entry.id, entry.category, entry.name, entry.amount] for entry in data]

    if request.method == "POST":
        if "exportCSV" in request.form:
            csv_data = services.export_to_csv()
            return csv_data.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=entries.csv'
            }

        if "importCSV" in request.form:
            csv_file = request.files.get('csv_file')
            if csv_file:
                import_csv.callback(csv_file=csv_file)

        if "Rechercher" in request.form:
            id = request.form.get('id')
            try:
                entry = get.callback(id=uuid.UUID(id))
                if entry:
                    searched = entry
                else:
                    message = "Entrée non trouvée"
            except (ValueError, TypeError):
                message = "Entrée non trouvée"
            except Exception as e:
                message = "Entrée non trouvée"

        if "Modifier" in request.form:
            id = request.form.get('id')
            nom = request.form.get('nom')
            prix = request.form.get('prix')
            categorie = request.form.get('categorie')
            update.callback(id=uuid.UUID(id), name=nom, amount=float(prix), category=categorie)
            if not models.update_entry(uuid.UUID(id), nom, float(prix), categorie):
                message = "Entrée non trouvée"

        if "Supprimer" in request.form:
            id = request.form.get('id')
            delete.callback(id=uuid.UUID(id))
            if not models.delete_entry(uuid.UUID(id)):
                message = "Entrée non trouvée"

    return render_template("getUpdateDelete.html", entries=entries, searched=searched, message=message)

@click.group()
def cli():
    pass

@cli.command()
def init_db():
    models.init_db()

@cli.command()
@click.option("-n", "--name", prompt="Name")
@click.option("-a", "--amount", type=float, prompt="Amount")
@click.option("-c", "--category", default=None)
def create(name: str, amount: float, category: Optional[str]):
    models.create_entry(name, amount, category)

@cli.command()
@click.option("--id", required=True, type=click.UUID)
def get(id: uuid.UUID):
    entry = models.get_entry(id)
    if entry:
        click.echo(entry)
    else:
        click.echo("Entry not found.")
    return entry

@cli.command()
@click.option("--as-csv", is_flag=True, help="Output a CSV string.")
def get_all(as_csv: bool):
    if as_csv:
        click.echo(services.export_to_csv().getvalue())
    else:
        for entry in models.get_all_entries():
            click.echo(entry)

@cli.command()
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    services.import_from_csv(csv_file)

@cli.command()
@click.option("--id", type=click.UUID, required=True)
@click.option("-n", "--name", required=True)
@click.option("-a", "--amount", type=float, required=True)
@click.option("-c", "--category", default=None)
def update(id: uuid.UUID, name: str, amount: float, category: Optional[str]):
    models.update_entry(id, name, amount, category)

@cli.command()
@click.option("--id", required=True, type=click.UUID)
def delete(id: uuid.UUID):
    models.delete_entry(id)

if __name__ == "__main__":
    app.run(debug=True)
