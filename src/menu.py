import pytermgui as ptg


def menu_pdf(all_element_in_folder: list) -> list:
    output = {}

    def submit(manager_window: ptg.WindowManager, window_terminal: ptg.Window) -> None:
        for widget in window_terminal:
            if isinstance(widget, ptg.InputField):
                output[widget.prompt] = widget.value
                continue

            if isinstance(widget, ptg.Container):
                label = widget[0]
                if len(widget) > 1:
                    field = widget[1]
                    output[label.value] = field.value
                else:
                    output[label.value] = ""

        manager_window.stop()

    def window(liste):
        config = """
           config:
               InputField:
                   styles:
                       prompt: dim italic
                       cursor: '@72'
               Label:
                   styles:
                       value: dim bold

               Window:
                   styles:
                       border: '60'
                       corner: '60'

               Container:
                   styles:
                       border: '96'
                       corner: '96'
           """

        with ptg.YamlLoader() as loader:
            loader.load(config)

        with ptg.WindowManager() as manager:
            input_fields = []
            for item in liste:
                input_fields.append(ptg.InputField("", prompt=f"{item}: "))

            _window = ptg.Window(
                ptg.Container(ptg.Label("Entrez une * \npour analyser le pdf"), ),
                *input_fields,
                ["Submit", lambda *_: submit(manager, _window)],
                width=60,
                box="DOUBLE",
            ).set_title("User Input").center()

            manager.add(_window)
            manager.run()

    # vérification que les éléments dans le dossier sont des pdf
    element_in_dir = [elt for elt in all_element_in_folder if len(elt) > 4 and elt[-4:] == ".pdf"]
    element_in_dir.append("TOUS LES ELEMENTS ")
    ######################################################################

    # Création de la fenêtre
    window(element_in_dir)
    ######################################################################

    selected_pdfs = []

    # Si "TOUS LES ELEMENTS : " a été sélectionné, ajout de tous les fichiers PDF
    if output["TOUS LES ELEMENTS : "] != "":
        selected_pdfs = element_in_dir[:-2]
    ######################################################################

    # Sinon, ajouter les fichiers PDF correspondant aux réponses
    else:
        for key, value in output.items():
            if key != "TOUS LES ELEMENTS : " and value != "":
                selected_pdfs.append(key.strip(': '))
    ######################################################################

    return selected_pdfs
