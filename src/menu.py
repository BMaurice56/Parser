import pytermgui as ptg
import os


def menuPdf(path: str) -> list:
    OUTPUT = {}

    def submit(manager: ptg.WindowManager, window: ptg.Window) -> None:
        for widget in window:
            if isinstance(widget, ptg.InputField):
                OUTPUT[widget.prompt] = widget.value
                continue

            if isinstance(widget, ptg.Container):
                label, field = iter(widget)
                OUTPUT[label.value] = field.value

        manager.stop()

    def window(liste):
        CONFIG = """
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
            loader.load(CONFIG)

        with ptg.WindowManager() as manager:
            input_fields = []
            for item in liste:
                input_fields.append(ptg.InputField("", prompt=f"{item}: "))

            window = (
                ptg.Window(
                    *input_fields,
                    ["Submit", lambda *_: submit(manager, window)],
                    width=60,
                    box="DOUBLE",
                )
                .set_title("User Input")
                .center()
            )

            manager.add(window)
            manager.run()

    # Example of usage

    element_in_dir = os.listdir(path)

    element_in_dir = [elt for elt in element_in_dir if len(elt) > 4 and elt[-4:] == ".pdf"]
    element_in_dir.append("TOUS LES ELEMENTS ")

    window(element_in_dir)

    selected_pdfs = []

    # Si "TOUS LES ELEMENTS : " a été sélectionné, ajouter tous les fichiers PDF
    if "TOUS LES ELEMENTS : " in OUTPUT and OUTPUT["TOUS LES ELEMENTS : "] == "y":
        selected_pdfs = [key.strip(': ') for key in OUTPUT.keys() if key != "TOUS LES ELEMENTS : "]

    # Sinon, ajouter les fichiers PDF correspondant aux réponses "y"
    else:
        for key, value in OUTPUT.items():
            if key != "TOUS LES ELEMENTS : " and value.lower() == "y":
                selected_pdfs.append(key.strip(': '))

    return selected_pdfs

