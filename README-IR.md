This repository uses the SSLRec framework to run experiments on the LightGCN 
recommendation model. More information on SSLRec acn be found on the 
[README-SSLRec.md](README.md) file.

We use the LightGCN implementation included by default in the SSLRec models directory.

### Requirements
See [README-SSLRec.md](README.md)
To install dgl: conda install -c dglteam/label/cu117 dgl
Additionally, install tensorboard using: conda install conda-forge::tensorboard
Might also need to install yaml: conda install pyyaml

### USAGE
See [README-SSLRec.md](README.md)
### Fine-tuning
To modify fine-tuning for LightGCN, use file [lightgcn.yml](config/modelconf/lightgcn.yml)

For information on formatting, see [User Guide.md](docs/User Guide.md)
