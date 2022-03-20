import logging
from py2neo import Graph
from dotenv import dotenv_values
from definitions import CONFIG_PATH
import numpy as np

logger = logging.getLogger(__name__)
config = dotenv_values(CONFIG_PATH)


#
# class ModelSevice(object):
#     def __init__(self, models_args):
#         self.models = OrderedDict()
#         self.models_args = models_args
#         self.gpus = tf.config.list_logical_devices('GPU')
#         self.cpus = tf.config.list_logical_devices('CPU')
#         # self._configure_gpus()
#         # self.init_model_from_ckpt(**self.models_args[-1])
#
#
#     def _build_empty_exp(self, model_id="chromato"):
#         config = self.models.get(model_id).get('config')
#         mol_names_input_ids = np.full((2, config.max_length_molecules), 0)
#         mol_names_input_attention_mask = np.full((2, config.max_length_molecules), 0)
#         atoms_ids = np.full((2, config.max_length_molecules, config.max_length_atoms), 0)
#         atoms_attention_mask = np.full((2, config.max_length_molecules, config.max_length_atoms), 0)
#         atoms_bonds = np.full((2, config.max_length_molecules, config.max_length_atoms, 2), [0, 0])
#         atoms_coords = np.full((2, config.max_length_molecules, config.max_length_atoms, 3), [0, 0, 0])
#         experiment = {}
#         experiment['atoms_coords'] = np.abs(atoms_coords)
#         experiment['atoms_ids'] = atoms_ids
#         experiment['bonds'] = atoms_bonds
#         experiment['atom_attention_mask'] = atoms_attention_mask
#         experiment['molecule_id'] = mol_names_input_ids
#         experiment['molecule_attention_mask'] = mol_names_input_attention_mask
#         return experiment
#
#     def resize_model_weights(self, model_id,new_size=None):
#
#         model = self.models.get(model_id).get('model')
#
#         tokenizer = self.models.get(model_id).get('tokenizer')
#         if model.config.vocab_size < len(tokenizer):
#             try:
#                 model(self._build_empty_exp(model_id))
#                 if not new_size:
#                     new_size=len(tokenizer)
#                 model.resize_token_embeddings(new_size)
#                 self.models.get(model_id).update({'model': model})
#             except Exception as exc:
#                 logger.error(exc)
#
#     def _configure_gpus(self):
#         gpus = tf.config.list_physical_devices('GPU')
#
#         if gpus:
#             try:
#                 # Currently, memory growth needs to be the same across GPUs
#                 for gpu in gpus:
#                     tf.config.experimental.set_memory_growth(gpu, True)
#                 logical_gpus = tf.config.experimental.list_logical_devices('GPU')
#                 logger.info(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
#             except RuntimeError as e:
#                 # Memory growth must be set before GPUs have been initialized
#                 logger.error(e)
#         if len(self.gpus) > 0:
#
#             self.default_device = self.gpus[-1].name
#         elif len(self.cpus) > 0:
#             self.default_device = self.cpus[-1].name
#
#     def train(self, model_id, TRAIN_CONF):
#         with tf.device('/device:GPU:1'):
#             strategy=TRAIN_CONF['strategy']
#
#             ckpt=self.models.get(model_id).get('ckpt')
#             model = self.models.get(model_id).get('model')
#             config = self.models.get(model_id).get('config')
#             manager =self.models.get(model_id).get('manager')
#             writer = self.models.get(model_id).get('writer')
#             tokenizer = self.models.get(model_id).get('tokenizer')
#             tokenizer_path = self.models.get(model_id).get('tokenizer_path')
#             mappings = self.models.get(model_id).get('mappings')
#             data = chemgan_utils.mapping_one_to_one_dict(TRAIN_CONF['paths']['EXPERIMENTS'], TRAIN_CONF['paths']['SAMPLES'],1000)
#             dynamic_arguments,dynamic_value_1,dynamic_value_2=TRAIN_CONF['params']
#             filters_input_mol_names = TRAIN_CONF['input_mol_names']
#             filters_input_mol_structures = TRAIN_CONF['input_mol_structures']
#             filter_output_mol_names = TRAIN_CONF['output_mol_names']
#             keys_to_exlude_str_transform=[]
#
#             if len(dynamic_arguments)>0 and len(dynamic_value_1)>0 and len(dynamic_value_2)>0:
#
#                 arguments_evaluluations, argument_eval_values = chemgan_utils.interpret_arguments(data, dynamic_arguments,
#                                                                                               dynamic_value_1,
#                                                                                               dynamic_value_2)
#                 for d,arg in zip(data,arguments_evaluluations):
#                     if d and arg:
#                         d.update(arg)
#                 filters_input_mol_names = filters_input_mol_names + ['ARG_LOGIC']
#                 keys_to_exlude_str_transform= keys_to_exlude_str_transform +['ARG_LOGIC']
#
#
#             # input_mol_names = chemgan_utils.filter_one_to_one(data, filters_input_mol_names)
#             name_path_mappings = chemgan_utils.find_and_convert_pymol(TRAIN_CONF['paths']['SAMPLES'],
#                                                                       TRAIN_CONF['paths']['CSPS'], data,
#                                                                       TRAIN_CONF['mol_str_keys_sample'],
#                                                                       TRAIN_CONF['mol_str_keys_csp'],
#                                                                       TRAIN_CONF['input_mol_structures'],
#                                                                       TRAIN_CONF['paths']['mol_dest_path'])
#
#             chemgan_utils.add_to_tokenizer(data, filters_input_mol_names, tokenizer, tokenizer_path,mappings,keys_to_exlude_str_transform)
#             chemgan_utils.add_to_tokenizer(data, filter_output_mol_names, tokenizer, tokenizer_path,
#                                            mappings)
#             chemgan_utils.add_to_tokenizer_mol_structures(name_path_mappings, tokenizer,
#                                                           tokenizer_path,
#                                                           mappings)
#             self.resize_model_weights(str(model_id))
#             iters_per_checkpoint = 250
#             batch_size = 1
#             for n in range(80000):
#                 for batch_data in chemgan_utils.chunks(data, batch_size):
#
#                     b_mol_names = chemgan_utils.filter_one_to_one(batch_data, filters_input_mol_names,keys_to_exlude_str_transform,transform=True)
#                     b_mol_names = [[v for k, v in v.items()] for v in [v for v in b_mol_names]]
#
#                     b_mol_structures = chemgan_utils.filter_one_to_one(batch_data, filters_input_mol_structures,transform=True)
#                     b_mol_structures = [[v for k, v in v.items()] for v in [v for v in b_mol_structures]]
#
#                     b_mol_names_output = chemgan_utils.filter_one_to_one(batch_data, filter_output_mol_names,transform=True)
#                     b_mol_names_output = [[v for k, v in v.items()] for v in [v for v in b_mol_names_output]]
#
#                     mol_names_input_ids, mol_names_input_attention_mask = chemgan_utils.tokenize_mol_names_batch(b_mol_names,
#                                                                                                                  tokenizer,
#                                                                                                                  config,
#                                                                                                                  batch_size)
#
#                     mol_names_output_ids, mol_names_output_attention_mask = \
#                         chemgan_utils.tokenize_mol_names_batch( b_mol_names_output, tokenizer, config, batch_size)
#
#                     atoms_ids, atoms_attention_mask, atoms_bonds, atoms_coords = chemgan_utils.tokenize_mol_structures(
#                         b_mol_structures, name_path_mappings,
#                         tokenizer, config, batch_size)
#
#                     experiment = {}
#                     experiment['atoms_coords'] = atoms_coords
#                     experiment['atoms_ids'] = atoms_ids
#                     experiment['bonds'] = atoms_bonds
#                     experiment['atom_attention_mask'] = atoms_attention_mask
#                     experiment['molecule_id'] = mol_names_input_ids
#                     experiment['molecule_attention_mask'] = mol_names_input_attention_mask
#                     labels = [[-100 if mask == 0 else token for mask, token in mask_and_tokens]
#                               for mask_and_tokens in
#                               [zip(masks, labels) for masks, labels in
#                                zip(mol_names_output_attention_mask,
#                                    mol_names_output_ids)]]
#                     output = model.train_chem((experiment, np.array(labels)))
#                     loss = output[0]
#                     logits = output[1]
#                     ckpt.step.assign_add(1)
#                     with writer.as_default():
#                         if int(ckpt.step) % (iters_per_checkpoint // 2) == 0:
#                             print(tf.reduce_mean(loss))
#                             try:
#                                 prediction = tf.argmax(logits, axis=-1)
#
#                                 tf.summary.text('Input ' + strategy,
#                                                 tokenizer.batch_decode(experiment['molecule_id'],skip_special_tokens=True)
#                                                 ,
#                                                 ckpt.step)
#                                 tf.summary.scalar("G_loss " + strategy, tf.squeeze(tf.reduce_mean(loss)), step=ckpt.step)
#                                 tf.summary.text('Prediction ' + strategy,  tokenizer.batch_decode(prediction,skip_special_tokens=True),
#                                                 ckpt.step)
#                                 tf.summary.text('Real ' + strategy,tokenizer.batch_decode(mol_names_output_ids,skip_special_tokens=True),
#                                                 ckpt.step)
#                             except Exception as exc:
#                                 print(exc)
#
#                     if int(ckpt.step) % iters_per_checkpoint == 0:
#                         try:
#                             save_path = manager.save()
#
#                             print("Saved checkpoint for step {}: {}".format(int(ckpt.step), save_path))
#                         except Exception as exc:
#                             print(exc)
#
#                     print('Input ' + strategy, tokenizer.batch_decode(experiment['molecule_id'],skip_special_tokens=True))
#                     prediction = tf.argmax(logits, axis=-1)
#
#
#                     print('Prediction ' + strategy, tokenizer.batch_decode(prediction,skip_special_tokens=True))
#                     print('Real ' + strategy,tokenizer.batch_decode(mol_names_output_ids,skip_special_tokens=True))
#                     print(tf.reduce_mean(loss))
#
#     def init_model_from_ckpt(self, **kwargs):
#
#      with tf.device('/device:GPU:1'):
#         config = kwargs.pop("config", None)
#         tokenizer_path = kwargs.pop('tokenizer_path', None)
#         for config_class, value in MODEL_CONFIG_MAPPING.items():
#             if isinstance(config, config_class):
#
#                 tokenizer_class = value.get("tokenizer_class")
#                 model_class = value.get("model_class")
#                 tokenizer_class.build_inputs_with_special_tokens = build_inputs_with_special_tokens
#                 tokenizer = tokenizer_class.from_pretrained(tokenizer_path)
#                 tokenizer.pad_token = tokenizer.unk_token
#                 config.vocab_size = len(tokenizer)
#
#                 mappings = {}
#                 if os.path.isfile(os.path.join(tokenizer_path, 'mappings.json')):
#                     if os.stat(os.path.join(tokenizer_path, 'mappings.json')).st_size > 0:
#                         with open(os.path.join(tokenizer_path, 'mappings.json'), 'r') as file:
#                             mappings = json.load(file)
#                 else:
#                     with open(os.path.join(tokenizer_path, 'mappings.json'), 'w') as file:
#                         json.dump(mappings, file)
#                 ckpt_path = kwargs.pop('ckpt_path')
#                 model = model_class(config)
#                 ep_cnt = tf.Variable(initial_value=0, trainable=False, dtype=tf.int64)
#                 ckpt = tf.train.Checkpoint(chemtransformer=model, step=ep_cnt)
#
#                 manager = tf.train.CheckpointManager(ckpt, ckpt_path, max_to_keep=1)
#                 writer = tf.summary.create_file_writer(os.path.join(ckpt_path, 'logs3'))
#                 ckpt.restore(manager.latest_checkpoint)
#                 if manager.latest_checkpoint:
#                     logger.info("Restored from {}".format(manager.latest_checkpoint))
#                 else:
#                     logger.info("Initializing from scratch.")
#
#                 if model and tokenizer:
#                     self.models.update({kwargs.pop('serving_name', model.__class__): {
#                         'model': model, 'config': config, 'tokenizer': tokenizer, 'tokenizer_path': tokenizer_path,
#                         'mappings': mappings,'manager':manager,'writer':writer,'ckpt':ckpt}})
#                     # model.s

class NeoConnection(object):
    def __init__(self, config):
        if config:
            self.graph = config
        else:
            raise Exception('missing_config', 'config')

    @property
    def graph(self):
        return self.__graph

    @graph.setter
    def graph(self, config):

        if len(np.intersect1d(['neouser', 'neopw', 'neourl'],[str(k) for k in config.keys()])) ==3:
            self.__graph = Graph(config.get("neourl"),user=config.get("neouser"), password=config.get("neopw"))
        else:
            raise Exception('missing_config', [str(k) for k in config.keys() if k not in ['neouser', 'neopw', 'neourl']])


neoconnection=NeoConnection(config)