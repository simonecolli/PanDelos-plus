#!/usr/bin/python3
import sys
import json
from Bio import SeqIO

path2gbks = sys.argv[1]
if path2gbks[len(path2gbks) - 1] != "/":
    path2gbks += "/"

path2clus = sys.argv[2]
outFilePath = sys.argv[3]




# path to gbk, salmo
def read_gbk(gbks):

    genome2cdstag = dict()
    cdstag2genome = dict()
    cdstag2product = dict()
    genesCoords = dict()
    sequences = dict()

    for genome_id in gbks.keys():
        ifile = gbks[genome_id]
        # print("genome_id:", genome_id)
        # print("ifile:", ifile)

        genome_cdslist = genome2cdstag.get(genome_id, list())

        for record in SeqIO.parse(ifile, "genbank"):
            sequence_id = record.id

            for feature in record.features:
                if (feature.type == 'CDS'):
                    if ('translation' in feature.qualifiers):

                        direction = "?"
                        strand = feature.location.strand
                        if strand == 1:
                            direction = "+"
                        elif strand == -1:
                            direction = "-"
                        tag = (genome_id, sequence_id, feature.qualifiers['locus_tag'][0])
                        
                        genome_cdslist.append(tag)
                        cdstag2genome[tag] = genome_id
                        cdstag2product[tag] = (feature.qualifiers['product'][0]).replace('\t','')
                        genesCoords[tag] = {
                            "strand": direction,
                            "start": feature.location.start,
                            "end": feature.location.end
                        }
                        # todo: save sequence
                        sequences[tag] = feature.qualifiers['translation'][0]

        genome2cdstag[genome_id] = genome_cdslist


    allGenesWithCoords = {}

    uniques = dict()
    # print("converting")

    for k in sorted(cdstag2genome.keys()):
        gen_id = k[0]+":"+k[1]
        if gen_id not in uniques:
            uniques[ gen_id ] = dict()
		
        uniques[ gen_id ][k[2]] = uniques[ gen_id ].get(k[2],0) + 1
        cc = uniques[ gen_id ][k[2]]

        # print("cc:",cc)
        acc = k[0]+":"+k[1]+":"+k[2]+":"+str(cc)
        # print(acc)
        current = {
            "complete-identifier": acc,
            "genome-name": k[0],
            "locus-version": k[1],
            "locus-tag": k[2],
            "product": cdstag2product[k],
            "coordinates": genesCoords[k],
            "sequence": sequences[k]
        }
        allGenesWithCoords[acc] = current
        # print(current)
    
    # print(allGenesWithCoords)
    return allGenesWithCoords






requiredFiles = dict()
encodedOut = []

with open(path2clus, "r") as clus:
    for line in clus.readlines():
        lineGenes = line.strip().split(" ")
        # print(lineGenes)

        # familyName = "family_" + lineGenes[0]
        currentFamily = dict()
        
        for gene in lineGenes:
            if "family-name" not in currentFamily:
                currentFamily["family-name"] = gene
                currentFamily["genes"] = list()
            
            splittedGene = gene.strip().split(":")


            # print(gene)
            # print(splittedGene)

            requiredFiles[splittedGene[0]] = path2gbks + splittedGene[0] + ".gbk"
            currentFamily["genes"].append(gene)

        # encodedOut[familyName] = currentFamily
        encodedOut.append(currentFamily)


# print(json.dump(requiredFiles))
# print(json.dumps(encodedOut, indent=4))

# print("Required files:", json.dumps(requiredFiles, indent=4))

allGenes = read_gbk(requiredFiles)
# print("All genes:", allGenes)

# print(json.dumps(allGenes, indent=4))




for family in encodedOut:
    # print(family)
    # print(family["genes"])

    genesTmp = list()
    for geneKey in family["genes"]:
        genesTmp.append(allGenes[geneKey])

    family["genes"] = genesTmp
    # for geneKey in encodedOut[family]["genes"]:
    #     # print(geneKey)

    #     encodedOut[family]["genes"][geneKey] = allGenes[geneKey]

print("Writing to", outFilePath)
with open(outFilePath, "w") as f:
    json.dump(encodedOut, f, indent=4)
