import sys
import json
import webbrowser
from PyQt5.QtWidgets import (QMainWindow, QComboBox, QLineEdit, QPushButton,
    QPlainTextEdit, QLabel, QAction, qApp, QWidget, QRadioButton, QGridLayout,
    QHBoxLayout, QGroupBox, QGroupBox, QMessageBox, QApplication)
from PyQt5.QtCore import Qt

save_file = "categoryData.json"
categories = {}

def main():
    app = QApplication(sys.argv)
    gui = GUI()
    err = load_json()
    if err:
        gui.showFileError(err)
    gui.updateDropdowns()
    gui.chooseFocus()
    sys.exit(app.exec_())

# save the dict as JSON to file
def save_json():
    try:
        with open(save_file, "w") as saved_data:
            json.dump(categories, saved_data)
    except IOError:
        return "save_error"

# load the dict as JSON from file
def load_json():
    # load file. if empty or non-existent, tell user
    try:
        with open(save_file, "r") as saved_data:
            global categories
            categories = json.load(saved_data)
    except IOError:
        # probably file doesn't exist, so try to create it
        return save_json()
    except json.decoder.JSONDecodeError:
        return "json_error"

def search(category, terms):
    if category in categories.keys():
        for url in categories[category]:
            # using simple string.replace to insert search terms
            url = url.replace("%s", terms)
            webbrowser.open(url, new=2)

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        instr = "Type URLs here. e.g. www.google.com/search?q=%s"

        self.searchDropdown = QComboBox(self)
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("Search terms")
        self.searchBox.textEdited.connect(self.checkSearchButtonEnable)
        self.searchBox.returnPressed.connect(self.searchClicked)
        self.searchButton = QPushButton("Search", self)
        self.searchButton.setEnabled(False)
        self.searchButton.clicked.connect(self.searchClicked)

        self.addNewRadio = QRadioButton(self)
        self.addNewRadio.toggled.connect(self.addRadioToggled)
        self.editRadio = QRadioButton(self)
        self.newCatBox = QLineEdit("", self)
        self.newCatBox.setPlaceholderText("New category name")
        self.newCatBox.textEdited.connect(self.checkSaveButtonEnable)
        self.editCatDropdown = QComboBox(self)
        self.editCatDropdown.currentIndexChanged[str].connect(self.editDropdownChanged)
        self.saveCatButton = QPushButton("Save", self)
        self.saveCatButton.clicked.connect(self.saveCatClicked)
        self.saveCatButton.setEnabled(False)
        self.deleteCatButton = QPushButton("Delete", self)
        self.deleteCatButton.clicked.connect(self.deleteCatClicked)
        self.urlBox = QPlainTextEdit(self)
        self.urlBox.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.urlBox.setPlaceholderText(instr)
        self.addNewRadio.setChecked(True)
        self.addNewChecked()

        mainWidget = QWidget()
        mainLayout = QGridLayout()
        topGrid = QGridLayout()
        topGroup = QGroupBox("Search")
        topGrid.setSpacing(8)
        topGrid.addWidget(self.searchDropdown, 0, 0, 1, 8)
        topGrid.addWidget(self.searchBox, 1, 0, 1, 8)
        topGrid.addWidget(self.searchButton, 1, 8, 1, 2)
        topGroup.setLayout(topGrid)
        mainLayout.addWidget(topGroup, 0, 0)

        bottomGrid = QGridLayout()
        bottomGroup = QGroupBox("Create or edit categories")
        addNewLayout = QHBoxLayout()
        addNewLayout.addWidget(self.addNewRadio)
        addNewLayout.addWidget(self.newCatBox)
        bottomGrid.addLayout(addNewLayout, 0, 0, 1, 8)
        editCatLayout = QHBoxLayout()
        editCatLayout.addWidget(self.editRadio)
        editCatLayout.addWidget(self.editCatDropdown, Qt.AlignLeft)
        bottomGrid.addLayout(editCatLayout, 1, 0, 1, 8)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.saveCatButton)
        buttonLayout.addWidget(self.deleteCatButton)
        bottomGrid.addWidget(self.urlBox, 2, 0, 5, -1)
        bottomGrid.addLayout(buttonLayout, 9, 6, 1, -1)
        bottomGroup.setLayout(bottomGrid)

        mainLayout.addWidget(bottomGroup, 1, 0)
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
        self.statusBar().showMessage("")

        exitAction = QAction("E&xit", self)
        exitAction.setShortcut("Esc") #Ctrl+Q
        exitAction.setStatusTip("Exit MultiSearch")
        exitAction.triggered.connect(qApp.quit)

        helpAction = QAction("&Help", self)
        helpAction.setShortcut("F1")
        helpAction.setStatusTip("Show Help")
        helpAction.triggered.connect(self.showHelp)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        helpMenu = menubar.addMenu("&Help")
        fileMenu.addAction(exitAction)
        helpMenu.addAction(helpAction)

        self.setGeometry(300, 300, 325, 425)
        self.setWindowTitle('MultiSearch')
        self.show()

    def showHelp(self):
        QMessageBox.information(self, "Instructions", "Categories must be created " \
            "before you can search.\nA category is a collection of URLs.\n" \
            "URLs should be placed on separate lines.\nURLs should contain \"%s\" " \
            "where the search terms will be substituted.\n" \
            "E.g. https://www.google.com/search?q=%s")

    def addRadioToggled(self, checked):
        if checked:
            self.addNewChecked()
            self.urlBox.clear()
        else:
            text = self.editCatDropdown.currentText()
            self.editChecked(text)
            self.populateURLs(text)

    def addNewChecked(self):
        self.newCatBox.setEnabled(True)
        self.editCatDropdown.setEnabled(False)
        self.deleteCatButton.setEnabled(False)

    def editChecked(self, text):
        self.newCatBox.setEnabled(False)
        self.editCatDropdown.setEnabled(True)
        self.checkDeleteButtonEnable(text)

    def searchClicked(self):
        searchTerms = self.searchBox.text()
        catName = self.searchDropdown.currentText()
        if searchTerms and catName:
            if catName:
                search(catName, searchTerms)

    def editDropdownChanged(self, text):
        if self.editRadio.isChecked():
            self.populateURLs(text)
            self.checkDeleteButtonEnable(text)

    def checkDeleteButtonEnable(self, text):
        if text and not self.deleteCatButton.isEnabled():
            self.deleteCatButton.setEnabled(True)
        elif not text and self.deleteCatButton.isEnabled():
            self.deleteCatButton.setEnabled(False)

    def populateURLs(self, text):
        if text in categories.keys():
            urlString = ""
            for url in categories[text]:
                if not urlString:
                    urlString += url
                else:
                    urlString += "\n" + url
            self.urlBox.setPlainText(urlString)
        else:
            self.urlBox.setPlainText("")

    #TODO: Clean up
    def saveCatClicked(self):
        isAddNew = False
        catName = ""
        #new cat
        if self.addNewRadio.isChecked():
            catName = self.newCatBox.text()
            if catName:
                catName = catName.lower()
                isAddNew = True
                if catName in categories.keys():
                    self.statusBar().showMessage("Category already exists. " \
                        "Select and edit it below.", 6000)
                    return
        #edit cat
        elif self.editRadio.isChecked():
            catName = self.editCatDropdown.currentText()
            if not catName:
                return

        urlsString = self.urlBox.toPlainText()
        if urlsString:
            urls = urlsString.split("\n")
        else:
            urls = []
        if catName:
            categories[catName] = urls
            err = save_json()
            if err:
                self.showFileError(err)
                return
            else:
                self.statusBar().showMessage("Saved", 3000)
        if isAddNew:
            self.updateDropdowns()
            self.newCatBox.clear()
            self.urlBox.clear()
        self.chooseFocus()

    def deleteCatClicked(self):
        category = self.editCatDropdown.currentText()
        if category:
            del categories[category]
            err = save_json()
            if err:
                self.showFileError(err)
            self.updateDropdowns()
            self.chooseFocus()
            if not self.editCatDropdown.currentText():
                self.addNewRadio.setChecked(True)
                self.newCatBox.setFocus()

    def updateDropdowns(self):
        self.searchDropdown.clear()
        self.editCatDropdown.clear()
        self.searchDropdown.addItems(categories.keys())
        self.editCatDropdown.addItems(categories.keys())

    def checkSearchButtonEnable(self, text):
        if text and not self.searchButton.isEnabled():
            self.searchButton.setEnabled(True)
        elif not text and self.searchButton.isEnabled():
            self.searchButton.setEnabled(False)

    def checkSaveButtonEnable(self, text):
        if text and not self.saveCatButton.isEnabled():
            self.saveCatButton.setEnabled(True)
        elif not text and self.saveCatButton.isEnabled():
            self.saveCatButton.setEnabled(False)

    def chooseFocus(self):
        if self.searchDropdown.currentText():
            self.searchBox.setFocus()
        else:
            self.newCatBox.setFocus()

    def showFileError(self, type):
        if type == "save_error":
            QMessageBox.warning(self, "File Error", "There was an error while "\
                "saving or creating the file.\nMultiSearch will now exit.")
        elif type == "json_error":
            QMessageBox.warning(self, "File Error", "There was an error reading "\
                "JSON from file.\nIf the file was edited manually, ensure proper "\
                "syntax is used.\nExit Multisearch and correct or delete the file.")
        qApp.exit(1)

if __name__ == '__main__':
    main()
