from jarvis.db.figshare import get_jid_data

from jarvis.core.atoms import Atoms

from jarvis.analysis.magnetism.magmom_setup import MagneticOrdering

 

jids = ["JVASP-882", "JVASP-943", "JVASP-858", "JVASP-17468", "JVASP-23213"]

 

jids = ["JVASP-23213"]

for jid in jids:

    d = get_jid_data(jid=jid, dataset="dft_3d")

    atoms = Atoms.from_dict(d["atoms"]).get_primitive_atoms

    symm_list, ss = MagneticOrdering(atoms=atoms).get_minimum_configs(min_configs=5)

 

    print( len(symm_list))
