# -*- coding: utf-8 -*-

import chainer
from chainer import Variable
from chainer import Chain, ChainList
import chainer.functions as F
import chainer.links as L

class ABS(Chain):
    '''
    ycは自分の出力なのかどうか疑問
    ここでは正解をycとして使う
    '''
    def __init__(self,
                 V_vocab_size,
                 D_embedding_size,
                 H_hidden_size,
                 C_window_size,
                 Q_smoothing_window,
                 dropout_ratio=0.0,
                 activate=F.tanh,
                 initial_EG_W=None,
                 initial_F_W=None,
                 return_p=False):
        
        super(ABS, self).__init__()
        self.dropout_ratio = dropout_ratio
        self.return_p = return_p
        self.H_hidden_size = H_hidden_size
        self.Q_smoothing_window = Q_smoothing_window
        pad_size_all = Q_smoothing_window - 1
        self.pad_size_former = pad_size_all // 2
        self.pad_size_latter = pad_size_all - self.pad_size_former
        self.activate = activate
   
        with self.init_scope():
            self.E = L.EmbedID(V_vocab_size, D_embedding_size, initialW=initial_EG_W, ignore_label=-1)
            self.F = L.EmbedID(V_vocab_size, H_hidden_size, initialW=initial_F_W, ignore_label=-1)
            self.G = L.EmbedID(V_vocab_size, D_embedding_size, initialW=initial_EG_W, ignore_label=-1)
            self.U = L.Linear(C_window_size*D_embedding_size, H_hidden_size)
            self.V = L.Linear(H_hidden_size, V_vocab_size)
            self.W = L.Linear(H_hidden_size, V_vocab_size)
            self.P = L.Linear(C_window_size*D_embedding_size, H_hidden_size)

    def __call__(self, x_yc):

        ### encoder ###
        xs = [Variable(self.xp.array(x, dtype=self.xp.int32)) for x, _ in x_yc]
        yc = Variable(self.xp.array([yc for _, yc in x_yc], dtype=self.xp.int32))
        
        tilde_xs = [self.F(x) for x in xs]
        
        tilde_dash_yc = self.G(yc)
        
        P_tilde_dash_yc = self.P(F.reshape(tilde_dash_yc, (tilde_dash_yc.shape[0], -1)))

        xPyc = [F.flatten(F.softmax(F.matmul(pyc, F.transpose(x)), axis=1)) for pyc, x in zip(F.split_axis(P_tilde_dash_yc, P_tilde_dash_yc.shape[0], axis=0), tilde_xs)]
        
        padded_xs = [F.concat((F.concat((F.broadcast_to(x[0], (self.pad_size_former, self.H_hidden_size)), x), axis=0), F.broadcast_to(x[-1], (self.pad_size_latter, self.H_hidden_size))), axis=0) for x in tilde_xs]

        bar_xs = [F.average_pooling_2d(F.expand_dims(F.expand_dims(x, axis=0), axis=1), ksize=(self.Q_smoothing_window, 1), stride=(1, 1), pad=0) for x in padded_xs]
        bar_xs = [F.squeeze(x, axis=(0, 1)) for x in bar_xs]
        
        enc = F.concat([F.matmul(F.expand_dims(p, axis=0), bar_x) for p, bar_x in zip(xPyc, bar_xs)], axis=0)

        if self.return_p:
            return xPyc, enc

        ### NLM ###
        tilde_yc = self.E(yc)

        h =  F.dropout(self.activate(self.U(tilde_yc)), ratio=self.dropout_ratio)

        ### Integrate ###
        y = F.dropout(self.V(h), ratio=self.dropout_ratio) + F.dropout(self.W(enc), ratio=self.dropout_ratio)
        
        return y
