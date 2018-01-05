import glob
import numpy as np

import chainer
from chainer import cuda
import chainer.links as L
from chainer import optimizers
from chainer import serializers

def getOptimizer(opt_config):
    optc = opt_config.copy()
    opt = optimizers.__dict__[opt_config.pop("name")]
    return opt(**opt_config)

def getModel(nn_module, nn_config):
    nnc = nn_config.copy()
    nnModel = nn_module.__dict__[nnc.pop("name")]
    return nnModel(**nnc)

def getModelNumber(model_path):
    template = model_path.replace("%epoch", '*')
    former = template.split('*')[0]
    latter = template.split('*')[1]
    list_path = glob.glob(template)
    arr_epoch = np.array([int(path.split(former)[1].split(latter)[0]) for path in list_path])
    arr_epoch.sort()
    return arr_epoch

def loadModel(model, model_path, epoch=None):
    if epoch is None:
        save_path = model_path
    else:
        save_path = model_path.format(epoch=epoch)
    serializers.load_npz(save_path, model)
    return model

def modelSetup(nn_module, nn_config, opt_config, model_path=None, epoch=None):  

    nn = getModel(nn_module, nn_config)
    model = L.Classifier(nn)
    
    if not model_path is None:
        model = loadModel(model, model_path, epoch)
        nn = model.predictor
        return nn, model, None

    optimizer = getOptimizer(opt_config["optimizer"])
    optimizer.setup(model)

    if opt_config["weight_decay"]:
        optimizer.add_hook(chainer.optimizer.WeightDecay(0.0005))

    return nn, model, optimizer

def cudaCheck():
    try:
        cuda.check_cuda_available()
        return cuda.cupy
    except RuntimeError:
        return np

def cudaSetup(model, env_config):
    try:
        gpu = env_config["gpu"]["main"]
        cuda.check_cuda_available()
        cuda.get_device(gpu).use()
        model.to_gpu()
        xp = cuda.cupy
        return xp, gpu, model
    except RuntimeError:
        env_config["gpu"]["main"] = -1
        return np, None, model

def saveModel(model, model_path, epoch):
    mdl = model.copy()
    mdl.to_cpu()
    save_path = model_path.replace("%epoch", "%d"%epoch)
    serializers.save_hdf5(save_path, mdl)
    del mdl
