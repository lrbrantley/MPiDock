#!/bin/python3
import csv
import argparse

parser = argparse.ArgumentParser(
    prog='accuracy',
    description='Compare the log files of idock and vina against each other or other runs of themself',
    usage='%(prog)s [acc] programFlag filePath [programFlag] filePath')
parser.add_argument('-a', '--acc', type=float, default=1.0,
    help="How different the ligands can be before being flagged as an error")
parser.add_argument('-v', '--Vina', nargs = '*',
    help="Location of Vina Output")
parser.add_argument('-i', '--iDock', nargs = '*',
    help="Location of iDock Output")

args = parser.parse_args()

#The actual comparison of the two files is done here
def dict_compare (dict1, dict2):
    var = args.acc   
    dict1_keys = set(dict1.keys())
    dict2_keys = set(dict2.keys())
    intersect_keys = dict2_keys.intersection(dict1_keys)

    modified = {o : (dict1[o], dict2[o]) for o in intersect_keys if (abs(float(dict2[o]) - float(dict1[o])) > var)}
    same = set(o for o in intersect_keys if (abs(float(dict2[o]) - float(dict1[o])) < var))

    return modified, same

#Allows Vina to be compared to iDock
def standardize_dict(vina_dict):

    for key in vina_dict.keys():
        if(key.startswith("inh_")):
            new_key = key.lstrip("inh_")
            vina_dict[new_key] = vina_dict.pop(key)

    for key in vina_dict.keys():        
        if(key.endswith(".pdbqt")):
            new_key = key.rstrip(".pdbqt")
            vina_dict[new_key] = vina_dict.pop(key)

    return vina_dict

def idock_txt_open(filepath):
    with open(filepath, mode='r') as idock:
        i_reader = csv.reader(idock, delimiter = "	")
        idock_dict = {rows[0].split(" ")[0]:rows[0].split(" ")[-1] for rows in i_reader}       
        
    idock_dict = standardize_dict(idock_dict)

    return idock_dict

#Please use the .csv that iDock will put out
def idock_csv_open(filepath):
    with open(filepath, mode='r') as idock:
        i_reader = csv.reader(idock)
        idock_dict = {rows[0]:rows[2] for rows in i_reader}

    return idock_dict

#Summary or Final Summary both will work 
def vina_open(filepath):
    with open(filepath, mode='r') as vina:
        v_reader = csv.reader(vina, delimiter = "	")
        vina_dict = {rows[0]:rows[1] for rows in v_reader}

    vina_dict = standardize_dict(vina_dict)

    return vina_dict

def main():
    
    #If no iDock Arguments, treat as an empty list  
    if args.iDock is None:
       args.iDock = []
      
    #If no Vina Arguments, treat as an empty list  
    if args.Vina is None:
       args.Vina = []
    
    #Empty line for formating
    print (" ")

    #Vina vs. iDock case  
    if len(args.iDock) == 1 and len(args.Vina) == 1:
        if args.iDock[0].endswith(".csv"):
            dict1 = idock_csv_open(args.iDock[0])
        else:
            dict1 = idock_txt_open(args.iDock[0])
        dict2 = vina_open(args.Vina[0])
        print ("iDock, Vina")

    #iDock vs. iDock case
    elif len(args.iDock) == 2 and len(args.Vina) == 0:
        if args.iDock[0].endswith(".csv"):
            dict1 = idock_csv_open(args.iDock[0])
        else:
            dict1 = idock_txt_open(args.iDock[0])
        
        if args.iDock[1].endswith(".csv"):
            dict2 = idock_csv_open(args.iDock[1])
        else:
            dict2 = idock_txt_open(args.iDock[1])
        print ("iDock1, iDock2")
    
    #Vina vs. Vina case
    elif len(args.iDock) == 0 and len(args.Vina) == 2:
       dict1 = vina_open(args.Vina[0])
       dict2 = vina_open(args.Vina[1])
       print ("Vina1, Vina2")
    
    #Error Case
    else:
       print ("Error, need two files")
       return
    
    #Create dictionary of modified ligands
    modified, same = dict_compare(dict1, dict2)
    
    #Print in Ligand Order
    for key in sorted(modified.keys()):
        print (key, modified[key])
    
main()
