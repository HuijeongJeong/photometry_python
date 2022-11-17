import functions.load as fnl

namespaces = ["C:\\Users\\Huijeong Jeong\\ndx-photometry-namlab\\spec\\ndx-photometry-namlab.namespace.yaml",
              "C:\\Users\\Huijeong Jeong\\ndx-eventlog-namlab\\spec\\ndx-eventlog-namlab.namespace.yaml"]

dandiset_id = '000351'
animalname = 'DB-longITI-C1-F1'
daylist = [1,2]

url, path = fnl.load_dandi_url(dandiset_id,animalname,daylist)
nwbfile = fnl.load_nwb(url[0],namespaces)
