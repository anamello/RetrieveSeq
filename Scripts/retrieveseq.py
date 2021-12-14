import requests, logging

class Ensembl():

    def __init__(self):

        self.server = "http://rest.ensembl.org"

    def get_species(self, division):

        search = "/info/species?content-type=application/json;hide_strain_info=1"

        if division == "Ensembl (main)":
            search += ";division=EnsemblVertebrates"
            r = requests.get(self.server+ search, headers={"Content-Type": "application/json"})
            decoded = r.json()

        else:
            search += ";division=" + division
            r = requests.get(self.server + search, headers={"Content-Type": "application/json"})
            decoded = r.json()


        list_names = []
        list_aliases = []

        if not r.ok:
            return r.ok

        else:
            for species in decoded['species']:
                list_aliases += species['aliases']
                list_names.append(species['name'])

            return (list_names, list_aliases)

    def get_stable_id(self, gene, species):

        '''
        Receives a gene symbol and looks for its stable ensembl ID.
        In case something goes wrong, returns boolean False.

        param gene: a string
        return: if everything went fine, a string
                else, boolean False
        '''

        logging.info("Getting stable Ensembl ID...")
        search = "/lookup/symbol/{}/{}?".format(species, gene)

        r = requests.get(self.server + search, headers={"Content-Type": "application/json"})

        # if an error occurs
        if not r.ok:
            logging.info('Stable ID not found.')
            logging.info('Check gene and species name. If everything is ok, try again. There might be a problem with the server.')
            return r.ok

        else:
            decoded = r.json()
            logging.info("Stable ID found: " + decoded['id'])
            return decoded['id']

    def getseq(self, id, type, upflank, downflank, format="text", multi_seq=0):

        '''
        Receives stable ID and type of sequence (CDS, UTR...)
        and looks for fasta sequence on Ensembl.
        In case something goes wrong, returns boolean False.

        param id: string
        param type: string
        return: if everything went fine, a string,
                else, boolean False
        '''

        if not id:
            return id

        else:
            if upflank !='0':
                seqsearch = "/sequence/id/{}?type={};expand_5prime={}".format(id, type, upflank)
            elif downflank != '0':
                seqsearch = "/sequence/id/{}?type={};expand_3prime={}".format(id, type, downflank)
            elif downflank != '0' and upflank != '0':
                seqsearch = "/sequence/id/{}?type={}expand_3prime={};expand_5prime={}".format(id, type, downflank, upflank)
            else:
                seqsearch = "/sequence/id/{}?type={}".format(id, type)

            #multiple sequences option
            seqsearch+=";multiple_sequences=" +str(multi_seq)

            if format == "json":
                r = requests.get(self.server + seqsearch, headers={"Content-Type": "application/json"})
                if not r.ok:
                    logging.info("Couldn't retrieve sequence.")
                    return r.ok
                else:
                    decoded = r.json()
                    return decoded

            else:
                r = requests.get(self.server + seqsearch, headers={"Content-Type": "text/x-fasta"})
                if not r.ok:
                    logging.info("Couldn't retrieve sequence.")
                    return r.ok
                else:
                    return r.text


    def getinfo(self, id):

        '''
        Looks for information of that ID on Ensembl.
        In case something goes wrong, returns boolean False

        param id: string
        return: if everything went fine, a dictionary
                else, boolean False
        '''

        search = "/lookup/id/" + id + "?"

        r = requests.get(self.server + search, headers={"Content-Type": "application/json"})

        if not r.ok:
            logging.info("Couldn't get info requested.")
            return r.ok

        else:
            decoded = r.json()
            return decoded

    def get_transcripts(self, id, type):

        '''
        Receives stable ID, looks for proteins from that ID on Ensembl,
        and returns IDs of all proteins found

        param id: string
        return: list
        '''

        logging.info("Finding all transcripts from gene...")
        seqinfo = self.getseq(id, type, '0', '0', format="json", multi_seq=1)
        if not seqinfo:
            return seqinfo

        else:
            trancript_ids = []
            for key in seqinfo:
                trancript_ids.append(key['id'])

            if trancript_ids:
                message = "Transcripts found: {}".format(' '.join(map(str, trancript_ids)))
                logging.info(message)
                return trancript_ids
            else:
                message = "No transcript found."
                logging.info(message)
                return False

    def select_transcript(self, id, type):

        '''
        Selects the transcript that is manually annotated and
        returns its fasta sequence. In case something
        goes wrong, returns boolean False

        param gene: string
        return: if everything went fine, a string
                else, boolean False
        '''

        if not id:
            return id
        else:
            transcripts = self.get_transcripts(id, type)

        if not transcripts:
            return transcripts
        else:
            logging.info("Selecting most canonical transcript...")
            flag2 = False
            flag = False
            for t in transcripts:
                transinfo = self.getinfo(t)
                if not transinfo:
                    return transinfo
                else:
                    try:
                        if transinfo['source'] == 'ensembl_havana' or transinfo['source'] == 'havana':
                            selected = t
                            logging.info("Transcript selected!")
                            flag2 = True
                            break
                    except KeyError:
                        flag = True
                        logging.info('Not able to check source of the sequence.')

            if flag2:
                return selected
            else:
                if flag:
                    logging.info('ATTENTION: Not able to check source of the sequence.')
                else:
                    logging.info('ATTENTION: No manually annotaded transcript was found.')

                return transcripts[0]

    def export_fasta(self, seq, gene, species, seqtype, savepath):

        '''
        Receives fasta sequence and gene symbol,
        and exports to fasta file.

        param seq: string
        param gene: string
        return: None
        '''

        logging.info("Exporting fasta file...")

        name = savepath + "/" + gene + "_" + species + "_" + seqtype + ".fas"
        outfile = open(name, 'w')

        split_seq = seq.split("\n")
        header = split_seq[0] + "; " + gene + '; ' + species + "; " + seqtype
        outfile.write(header+'\n')

        for line in split_seq[1:]:
            outfile.write(line+'\n')
        outfile.close()

    def export_multifasta(self, seqdict, savepath, seqtype, gene="multi_genes", species=""):

        name = savepath + "/" + gene + '_' + species + "_" + seqtype + ".fas"
        outfile = open(name, 'w')

        for info in seqdict:
            split_seq = seqdict[info].split("\n")
            genename = info[0]
            sp = info[2]
            type = info[3]
            header = split_seq[0] + "; " + genename + '; ' + sp + "; " + type

            outfile.write(header+'\n')
            for line in split_seq[1:]:
                outfile.write(line+'\n')

        logging.info("Successfully exported!\n")

        outfile.close()


#class NCBI(object):

