import re, webbrowser, logging
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from threading import Thread
from datetime import datetime
from Scripts.retrieveseq import Ensembl
from PIL import Image,ImageTk

class MainApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # set style for titles
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold")
        self.title('RetrieveSeq')
        self.geometry('530x450')

        # set style
        self.style = ttk.Style()
        # ('clam', 'alt', 'default', 'classic')
        self.style.theme_use("clam")

        #set color for progress bar
        self.style.configure("red.Horizontal.TProgressbar", foreground='#CA3D3F', background='#CA3D3F')

        # set font for messagebox
        font1 = tkfont.Font(name='TkCaptionFont', exists=True)
        font1.config(family='Arial', size=12, weight="normal")

        # set window icon
        #img = tk.PhotoImage(file='Icon/logo.png')
        #self.wm_iconphoto(True, img)

        #img = tk.Image("photo", file="/home/anamello/Documentos/agnis_project/retrieve_seq/Icon/retrieveseq-04.gif")
        #self.tk.call('wm', 'iconphoto', self._w, img)

        # The container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, EnsemblPage, NCBIPage, OutputPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def get_page(self, page_class):

        '''Get page for the given page name'''
        return self.frames[page_class]

    def validate_gene_entry(self, entry, type):
        ''' Validate user entry '''

        self.genelist = [x.strip() for x in entry.split(',')]
        self.entry_type = type

        # regex to test if entry is ok
        regex = re.compile('^([0-9A-Za-z./\s\-_]+)(\s?,\s?[0-9A-Za-z./\s\-_]+)*$')
        message = "Something is wrong with your entry. Please, write or paste genes separated by comma."

        if re.match(regex, entry):
            return True
        else:
            return message

    def disable_species_entry(self, choice):
        page = self.get_page("EnsemblPage")
        if choice == "Gene ID":
            page.speciesentry.delete("1.0",'end-1c')
            page.speciesentry.insert(tk.END, 'No need for species entry')
            page.speciesentry.configure(state="disabled", bg='#DCDAD5', fg="#9D9A9B")

        else:
            page.speciesentry.configure(state="normal", bg='white', fg="black")
            page.speciesentry.delete("1.0",'end-1c')


    def wrong_entry_popup(self, message):
        '''Show warning popup when entry is wrong'''

        messagebox.showwarning(title="Wrong Entry", message=message)

    def decide_next_button(self, bool, page_name):
        '''When clicking button -next-, decides if entry is ok or not to proceed '''

        if bool == True:
            self.show_frame(page_name)
        else:
            self.wrong_entry_popup(bool)

    def save_path_dialog(self):
        '''Open popup to select directory'''

        save_path = filedialog.askdirectory(title="Select output directory")
        return save_path

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # configure columns
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        # configure rows
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)

        # Retrieveseq logo
        logo = Image.open('Images/logo.png')
        resized_logo = logo.resize((200, 144), Image.ANTIALIAS)
        new_logo = ImageTk.PhotoImage(resized_logo)
        showlogo = ttk.Label(self, image=new_logo)
        showlogo.image = new_logo #keep reference
        showlogo.grid(row=0, columnspan=4)

        # title of the page
        pagetitle = ttk.Label(self, text="Welcome to RetrieveSeq!", font=controller.title_font)
        pagetitle.grid(row=1, columnspan=4)

        # instruction to first entry - gene symbols
        pastegenes = ttk.Label(self, text="Paste here the genes (symbol or ID) separated by comma.\n(Ex.: BRCA2,ASPM,RELN)", justify="center")
        pastegenes.grid(row=2, columnspan=4)

        # text box to paste the genes
        textbox = tk.Text(self, width = 60, height=3)
        textbox.grid(row=3, columnspan=4, sticky="NS", padx=(0,10))

        # create a Scrollbar and associate it with txt
        scrollb = ttk.Scrollbar(self, command=textbox.yview)
        scrollb.grid(columnspan=4, row=3, sticky="NS", padx=(490,0))
        textbox['yscrollcommand'] = scrollb.set

        # instruction to database selection
        selectdb = ttk.Label(self, text="Database:")
        selectdb.grid(column=0, row=4, sticky="E", padx=(0,10))

        # select database drop down menu
        dboptions = ['Ensembl']
        selected_db = tk.StringVar()
        #selected_db.set(dboptions[0])
        dropmenu = ttk.OptionMenu(self, selected_db, dboptions[0], *dboptions)
        dropmenu.grid(column = 1, row=4, sticky="W")

        # instruction to entry type selection
        selectentry = ttk.Label(self, text="Entry type:")
        selectentry.grid(column=2, row=4, sticky="E", padx=(0,10))

        # select entry type drop down menu
        entryoptions = ['Gene symbol', 'Gene ID']
        selected_entry = tk.StringVar()
        #selected_db.set(dboptions[0])
        dropmenu_entry = ttk.OptionMenu(self, selected_entry, entryoptions[0], *entryoptions, command=controller.disable_species_entry)
        dropmenu_entry.grid(column = 3, row=4, sticky="W")

        # Button for next page depending on selected database
        button_next = ttk.Button(self, text="Next",
                                command=lambda: controller.decide_next_button(controller.validate_gene_entry(textbox.get("1.0", 'end-1c'), selected_entry.get()),
                                                                                selected_db.get()+"Page"))
        button_next.grid(row = 5, columnspan=4)


class OutputPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # configure columns
        self.columnconfigure(0, weight=1)

        # configure rows
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)

        # Retrieveseq logo
        logo = Image.open('Images/logo.png')
        resized_logo = logo.resize((200, 144), Image.ANTIALIAS)
        new_logo = ImageTk.PhotoImage(resized_logo)
        showlogo = ttk.Label(self, image=new_logo)
        showlogo.image = new_logo #keep reference
        showlogo.grid(row=0)

        # Page title
        label = tk.Label(self, text="Retrieving your sequences", font=controller.title_font)
        label.grid(row=1)

        # processing bar
        self.progressLabel = tk.Label(self, text='Starting...')
        self.progressLabel.grid(row=2, sticky="S")
        self.progressBar = ttk.Progressbar(self, style="red.Horizontal.TProgressbar", orient="horizontal", length=400,mode="determinate")
        self.progressBar.grid(row=3, sticky="NS")
        self.progressBar['value'] = 0

        # button to go back to start page (disabled)
        self.button = ttk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        self.button.grid(row=4)
        self.button['state'] = 'disabled'

    def update_progressbar(self, Progress, Action):

        self.progressLabel.destroy()
        self.progressLabel = tk.Label(self, text=Action)
        self.progressLabel.grid(row=2, sticky="S")
        self.progressBar = ttk.Progressbar(self, style="red.Horizontal.TProgressbar", orient="horizontal", length=400, mode="determinate")
        self.progressBar.grid(row=3, sticky="NS")
        self.progressBar['value'] = Progress

class EnsemblPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.save_path = None
        self.selected_species = None
        self.selected_type = None
        self.upflank = None
        self.downflank = None
        self.trans_number = None
        self.file_format = None
        self.ensembl_division = None

        # Grid configuration (columns)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Grid configuration (rows)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=1)
        self.rowconfigure(7, weight=1)
        self.rowconfigure(8, weight=1)

        # page title
        pagetitle = tk.Label(self, text="Ensembl - Export Fasta Configuration", font=controller.title_font)
        pagetitle.grid(row=0, columnspan=2)

        # instruction to database selection
        selectdivision = tk.Label(self, text="Ensembl database:")
        selectdivision.grid(column=0, row=1, padx=(10,110))

        # select database drop down menu
        divisionoptions = ['Ensembl (main)', 'EnsemblMetazoa', 'EnsemblPlants', 'EnsemblFungi', 'EnsemblProtists', 'EnsemblBacteria']
        self.selected_division = tk.StringVar()
        #selected_db.set(dboptions[0])
        divisionmenu = ttk.OptionMenu(self, self.selected_division, divisionoptions[0], *divisionoptions)
        divisionmenu.grid(column = 1, row=1, sticky="WE", padx=10)

        # instruction to species selection
        choosespecies = tk.Label(self, text="Species")
        choosespecies.grid(column=0, row=2, padx=(10,180))

        # url to see species list
        link_species = tk.Label(self, text="(see list of species):", fg="grey", cursor="hand2")
        link_species.grid(column=0, row=2, padx=(15,0))
        link_species.bind("<Button-1>", lambda e: self.decide_species_url(self.selected_division.get()))
        f = tkfont.Font(link_species, link_species.cget("font"))
        f.configure(underline=True)
        link_species.configure(font=f)

        # entry box for species
        self.speciesentry = tk.Text(self, width = 20, height=2)
        self.speciesentry.grid(column=1, row=2, sticky="NSEW", padx=(10,20))

        # create a Scrollbar and associate it with txt
        scroll_species = ttk.Scrollbar(self, command=self.speciesentry.yview)
        scroll_species.grid(column=1, row=2, sticky="NS", padx=(230,0))
        self.speciesentry['yscrollcommand'] = scroll_species.set

        # instruction to 5' upstream selection
        upstream = tk.Label(self, text="5' Flanking sequence (upstream):")
        upstream.grid(column=0, row=3, padx=(10,15))

        # entry box for 5' upstream
        self.upentry = ttk.Entry(self)
        self.upentry.insert(0, "0")
        self.upentry.grid(column=1, row=3, sticky="WE", padx=10)

        # instruction to 3' downstream selection
        downstream = tk.Label(self, text="3' Flanking sequence (downstream):")
        downstream.grid(column=0, row=4, padx=(10,0))

        # entry box for 3' downstream
        self.downentry = ttk.Entry(self)
        self.downentry.insert(0, "0")
        self.downentry.grid(column=1, row=4, sticky="WE", padx=10)

        # instruction to sequence type selection
        selecttype = tk.Label(self, text="Sequence type:")
        selecttype.grid(column=0, row=5, padx=(10,125))

        # select database drop down menu
        seqoptions = ['Genomic', 'cDNA', 'Coding Sequence', 'Peptide Sequence']
        self.type_selection = tk.StringVar()
        #type_selection.set(seqoptions[0])
        dropmenu_seq = ttk.OptionMenu(self, self.type_selection, seqoptions[0], *seqoptions, command=self.disable_trans_selection)
        dropmenu_seq.grid(column=1, row=5, sticky="WE", padx=10)

        # instruction to how many transcripts selection
        selecttrans = tk.Label(self, text="How many transcripts per gene?")
        selecttrans.grid(column=0, row=6, padx=(10,15))

        # select how many transcripts
        transoptions = ['All transcripts', 'The most canonical']
        self.trans_selection = tk.StringVar()
        self.trans_selection.set(transoptions[0])
        self.dropmenu_trans = ttk.OptionMenu(self, self.trans_selection, transoptions[0], *transoptions)
        self.dropmenu_trans.grid(column=1, row=6, sticky="WE", padx=10)
        self.dropmenu_trans.configure(state="disabled")

        # instruction to format selection
        selectfasta = tk.Label(self, text="File format:")
        selectfasta.grid(column=0, row=7, padx=(10,150))

        # select format
        fastaoptions = ['Genes in separated files', 'All genes in one file']
        self.fasta_selection = tk.StringVar()
        self.fasta_selection.set(fastaoptions[0])
        self.dropmenu_fasta = ttk.OptionMenu(self, self.fasta_selection, fastaoptions[0], *fastaoptions)
        self.dropmenu_fasta.grid(column=1, row=7, sticky="WE", padx=10)

        # button to go back to start page
        back_button = ttk.Button(self, text="Back To Start Page",
                           command=lambda: controller.show_frame("StartPage"))
        back_button.grid(column=0, row=8)

        # button to proceed
        export_button = ttk.Button(self, text="Export Sequences",
                           command=lambda: self.clicked())
        export_button.grid(column=1, row=8)

    #############
    # Functions #
    #############

    def disable_trans_selection(self, choice):
        if choice != "Genomic":
            self.dropmenu_trans.configure(state="normal")
        else:
            self.dropmenu_trans.configure(state="disabled")

    def decide_species_url(self, division):

        if division == "Ensembl (main)":
            speciesurl = "http://ensembl.org/info/about/species.html"
        else:
            speciesurl = "http://"+division[7:]+".ensembl.org/species.html"

        webbrowser.open_new(speciesurl)

    def validate_flank_entry(self, entryup, entrydown):

        self.upflank = entryup
        self.downflank = entrydown

        message1="Maximum of 1000000 for flanking sequence"
        message2="You must enter only numbers for flanking sequence. Maximum = 1000000"

        if entryup.isnumeric() and entrydown.isnumeric():
            if int(entryup) <= 1000000 and int(entrydown) <= 1000000:
                return True
            else:
                return message1
        else:
            return message2

    def validate_species(self, entry):

        lower_entry = entry.lower()
        if lower_entry == "no need for species entry":
            self.selected_species = None
            return True

        else:
            species_info = Ensembl().get_species(self.ensembl_division)

            if not species_info:
                message3 = "Not able to check whether species exist in database. Try again."
                return message3

            else:
                list_names = species_info[0]
                list_aliases = species_info[1]

                if lower_entry == "all":
                    self.selected_species = list_names
                    return True

                else:
                    # regex to test if entry is ok
                    regex = re.compile('^([0-9A-Za-z./\s\-_]+)(\s?,\s?[0-9A-Za-z./\s\-_]+)*$')
                    message1 = "Something is wrong with your species entry. Please, write or paste species names separated by comma."

                    if re.match(regex, lower_entry):
                        species_list = [x.strip() for x in lower_entry.split(',')]
                        self.selected_species = species_list

                        not_found = []
                        for name in species_list:
                            if name not in list_names and name not in list_aliases:
                                not_found.append(name)

                        if not_found:
                            message2 = "Can't find species <{}> in {} database".format(', '.join(map(str, not_found)), self.ensembl_division)
                            return message2
                        else:
                            return True
                    else:
                        return message1


    def validate_type(self, entry):

        if entry == "Genomic":
            self.selected_type = 'genomic'

        elif entry == 'cDNA':
            self.selected_type = 'cdna'

        elif entry == 'Coding Sequence':
            self.selected_type = 'cds'

        elif entry == 'Peptide Sequence':
            self.selected_type = 'protein'

        return self.selected_type

    def retrieveseq(self, genelist, entrytype, savepath, specieslist, seqtype, upflank, downflank, opnumber, opformat):

        seqdict = {}
        njobs = len(genelist)

        progress = 0
        page = self.controller.get_page('OutputPage')

        if entrytype == "Gene ID":
            for id in genelist:
                logging.info("\n--" + id + "--")
                info = Ensembl().getinfo(id)

                if not info:
                    logging.info("Check if gene ID is correct.")
                    logging.info("{} was not downloaded.".format(id))
                    continue
                else:
                    species = info['species']

                if seqtype == 'genomic':
                    # register in log file
                    logging.info("Retrieving {} sequence...".format(seqtype))
                    progress += (70 / njobs)
                    page.update_progressbar(progress, 'Retrieving {} sequence'.format(id))
                    app.update_idletasks()
                    fasta = Ensembl().getseq(id, seqtype, upflank, downflank, 'text')
                    Ensembl().export_fasta(fasta, id, species, seqtype, savepath)
                    logging.info(id + " successfully downloaded!\n")

                # other types
                else:
                    if opnumber == "All transcripts":
                        # update progress bar
                        progress += 20 / njobs
                        page.update_progressbar(progress, 'Getting {} transcripts'.format(id))
                        app.update_idletasks()

                        # function
                        translist = Ensembl().get_transcripts(id, seqtype)

                        for transcript in translist:
                            # update progress bar
                            progress += (20 / njobs) / len(translist)
                            page.update_progressbar(progress, 'Retrieving transcripts sequences'.format(id))
                            app.update_idletasks()

                            # function
                            fasta = Ensembl().getseq(transcript, seqtype, upflank, downflank)
                            if not fasta:
                                # register in log file
                                logging.info(id + " was not retrieved.\n")
                            else:
                                if (id, transcript, species, seqtype) not in seqdict:
                                    seqdict[(id, transcript, species, seqtype)] = fasta

                        if opformat == 'Genes in separated files':
                            # register in log file
                            logging.info("Exporting multifasta file...\n")

                            # function
                            Ensembl().export_multifasta(seqdict, savepath, seqtype, species = species, gene=id)
                            seqdict = {}


                    else:  # only most canonical transcript
                        # progress bar update
                        progress += 30 / njobs
                        page.update_progressbar(progress,
                                                'Retrieving {} most canonical transcript sequence'.format(id))
                        app.update_idletasks()

                        # functions
                        transcript = Ensembl().select_transcript(id, seqtype)
                        fasta = Ensembl().getseq(transcript, seqtype, upflank, downflank)

                        if opformat == 'Genes in separated files':
                            # exporting
                            if not fasta:
                                logging.info(id + " was not downloaded.\n")
                            else:
                                # progress bar update
                                progress += 40 / njobs
                                page.update_progressbar(progress, 'Exporting {} fasta file'.format(id))
                                app.update_idletasks()
                                Ensembl().export_fasta(fasta, id, species, seqtype, savepath)

                                # register in log file
                                logging.info(id + " successfully downloaded!\n")

                        else:
                            if not fasta:
                                logging.info(id + " was not retrieved in multifasta file.\n")
                            else:
                                logging.info(id + " successfully retrieved.\n")
                                if (id, transcript, species, seqtype) not in seqdict:
                                    seqdict[(id, transcript, species, seqtype)] = fasta

            if not seqdict == {}:
                # register in log file
                logging.info("Exporting multifasta file...\n")

                # progress bar update
                progress += 70 / njobs
                page.update_progressbar(progress, 'Exporting multifasta file')
                app.update_idletasks()

                # call function
                Ensembl().export_multifasta(seqdict, savepath, seqtype)


        # if entry_type is gene symbol, must look for gene ID first
        else:
            yjobs = len(specieslist)
            for species in specieslist:
                logging.info("##########" + species + "#########")
                for gene in genelist:
                    logging.info("--" + gene + "--")
                    progress += (10/njobs)/yjobs
                    page.update_progressbar(progress, 'Getting {} Stable ID'.format(gene))
                    app.update_idletasks()
                    id = Ensembl().get_stable_id(gene, species)

                    # if id is not found
                    if not id:
                        logging.info(gene + " was not downloaded.\n")

                    # found id
                    else:
                        # if selected type is genomic
                        if seqtype == 'genomic':
                            # register in log file
                            logging.info("Retrieving {} sequence...".format(seqtype))
                            progress += (70/njobs)/yjobs
                            page.update_progressbar(progress, 'Retrieving {} sequence'.format(gene))
                            app.update_idletasks()
                            fasta = Ensembl().getseq(id, seqtype, upflank, downflank, 'text')
                            Ensembl().export_fasta(fasta, gene, species, seqtype, savepath)
                            logging.info(gene + " successfully downloaded!\n")

                        # other types
                        else:
                            if opnumber == "All transcripts":
                                # update progress bar
                                progress += (20/njobs)/yjobs
                                page.update_progressbar(progress, 'Getting {} transcripts'.format(gene))
                                app.update_idletasks()

                                # function
                                translist = Ensembl().get_transcripts(id, seqtype)

                                for transcript in translist:
                                    # update progress bar
                                    progress += ((20/njobs)/yjobs)/len(translist)
                                    page.update_progressbar(progress, 'Retrieving transcripts sequences'.format(gene))
                                    app.update_idletasks()

                                    #function
                                    fasta = Ensembl().getseq(transcript, seqtype, upflank, downflank)
                                    if not fasta:
                                        # register in log file
                                        logging.info(gene + " was not retrieved.\n")
                                    else:
                                        if (gene, transcript, species, seqtype) not in seqdict:
                                            seqdict[(gene, transcript, species, seqtype)] = fasta

                                if opformat == 'Genes in separated files':
                                    # register in log file
                                    logging.info("Exporting multifasta file...\n")

                                    # function
                                    Ensembl().export_multifasta(seqdict, savepath, seqtype, gene=gene, species=species)
                                    seqdict = {}

                            else: #only most canonical transcript
                                # progress bar update
                                progress += (30/njobs)/yjobs
                                page.update_progressbar(progress, 'Retrieving {} most canonical transcript sequence'.format(gene))
                                app.update_idletasks()

                                # functions
                                transcript = Ensembl().select_transcript(id, seqtype, species)
                                fasta = Ensembl().getseq(transcript, seqtype, upflank, downflank)

                                if opformat == 'Genes in separated files':
                                    # exporting
                                    if not fasta:
                                        logging.info(gene + " was not downloaded.\n")
                                    else:
                                        # progress bar update
                                        progress += (40/njobs)/yjobs
                                        page.update_progressbar(progress, 'Exporting {} fasta file'.format(gene))
                                        app.update_idletasks()
                                        Ensembl().export_fasta(fasta, gene, species, seqtype, savepath)

                                        # register in log file
                                        logging.info(gene + " successfully downloaded!\n")

                                # if format == genes in same file
                                else:
                                    if not fasta:
                                        logging.info(gene + " was not retrieved in multifasta file.\n")
                                    else:
                                        logging.info(gene + " successfully retrieved.\n")
                                        if (gene, transcript, species, seqtype) not in seqdict:
                                            seqdict[(gene, transcript, species, seqtype)] = fasta

                # export multifasta in case option selected is all genes in same file
                if not seqdict == {}:
                    # register in log file
                    logging.info("Exporting multifasta file...")

                    # progress bar update
                    progress += (70/njobs)/yjobs
                    page.update_progressbar(progress, 'Exporting multifasta file')
                    app.update_idletasks()

                    #call function
                    Ensembl().export_multifasta(seqdict, savepath, seqtype, species=species)

        # everything done
        logging.info("\nDone!")

    def ensembl_export(self):

        # Get output page
        page = self.controller.get_page('OutputPage')

        #configure log file
        timestamp = str(datetime.now()).replace(" ", "_")[:19]
        logname = "/retrieveseq_{}.log".format(timestamp.replace(":", "-"))

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(filename=self.save_path + logname, level=logging.INFO, format='%(message)s')

        # export sequences
        self.retrieveseq(self.controller.genelist,
                         self.controller.entry_type,
                         self.save_path,
                         self.selected_species,
                         self.selected_type,
                         self.upflank,
                         self.downflank,
                         self.trans_number,
                         self.file_format)

        # update progress bar
        page.update_progressbar(100, 'Finished')
        app.update_idletasks()

        # enable OutputPage button to go to start page (previously disabled)
        page.button['state'] = 'normal'

    def clicked(self):

        # get variables
        self.ensembl_division = self.selected_division.get()
        flank_valid = self.validate_flank_entry(self.downentry.get(), self.upentry.get())
        species_valid = self.validate_species(self.speciesentry.get("1.0",'end-1c'))
        self.validate_type(self.type_selection.get())
        self.trans_number = self.trans_selection.get()
        self.file_format = self.fasta_selection.get()

        if flank_valid == True and species_valid == True:
            # open save path popup
            self.save_path = self.controller.save_path_dialog()

            if not self.save_path:
                pass
            else:
                # go to output page
                self.controller.show_frame("OutputPage")

                # execute main function in new thread
                Thread(target=self.ensembl_export,).start()

        elif flank_valid == True and species_valid != True:
            self.controller.wrong_entry_popup(species_valid)
        elif flank_valid != True and species_valid == True:
            self.controller.wrong_entry_popup(flank_valid)
        else:
            self.controller.wrong_entry_popup(flank_valid)



class NCBIPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is NCBI page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = ttk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

# main loop
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()


