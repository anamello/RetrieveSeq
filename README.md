# RetrieveSeq (beta)
RetrieveSeq is a GUI application that performs batch download of how many gene sequences you wish from Ensembl database. Mind you: this application is still in development. Our goal is to increase its functions, as well as provide more database options.

## Dependencies

In order to properly run RetrieveSeq BETA, you need to have the following tools installed in your device:
- Python3
- Pillow (Python3 library). To install Pillow, open the terminal and type:

	$ sudo pip3 install Pillow

## Running RetrieveSeq

Open the terminal in the application folder and type the following:

	$ python3 main.py

Ps.: you might need to change permission before running:

	$ chmod a+x main.py

## Using RetrieveSeq

- Type or paste the gene symbols or gene ID separated by comma (anything else won't work) in the genes entry box.
- RetrieveSeq BETA only works with gene symbol or gene ID!
- In the next page, configure your output file(s).
- When downloading data via gene symbol, you can download selected genes for one species or more, just paste or type species separated by comma in the entry box. If you want to download genes for all species in the database, type "all" in the species entry box.
- A log file will be saved in the same directory you choose to save the genes. While running, RetrieveSeq BETA saves useful information in the log file (ex.: why determined gene can't be downloaded).
