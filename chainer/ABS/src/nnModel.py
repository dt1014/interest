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
                 return_enc=False):
        
        super(ABS, self).__init__()
        self.dropout_ratio = dropout_ratio
        self.return_enc = return_enc
        self.H_hidden_size = H_hidden_size
        self.Q_smoothing_window = Q_smoothing_window
        pad_size_all = Q_smoothing_window - 1
        self.pad_size_former = pad_size_all // 2
        self.pad_size_latter = pad_size_all - self.pad_size_former
        self.activate = activate
        
        with self.init_scope():
            self.E = L.EmbedID(V_vocab_size, D_embedding_size, ignore_label=-1)
            self.F = L.EmbedID(V_vocab_size, H_hidden_size, ignore_label=-1)
            self.G = L.EmbedID(V_vocab_size, D_embedding_size, ignore_label=-1)
            self.U = L.Linear(C_window_size*D_embedding_size, H_hidden_size)
            self.V = L.Linear(H_hidden_size, V_vocab_size)
            self.W = L.Linear(H_hidden_size, V_vocab_size)
            self.P = L.Linear(C_window_size*D_embedding_size, H_hidden_size)

    def __call__(self, x_yc):

        
        ### encoder ###
        xs = [Variable(self.xp.array(x, dtype=self.xp.int32)) for x, _ in x_yc]
        yc = Variable(self.xp.array([yc for _, yc in x_yc], dtype=self.xp.int32))

        print("yc")
        print(yc.shape)
        
        tilde_xs = [self.F(x) for x in xs]
        print("tilde_xs")
        print([i.shape for i in tilde_xs])
        
        tilde_dash_yc = self.G(yc)
        print("tilde_dash_yc")
        print(tilde_dash_yc.shape)
        print(F.reshape(tilde_dash_yc, (50, -1)).shape)
        
        P_tilde_dash_yc = self.P(F.reshape(tilde_dash_yc, (tilde_dash_yc.shape[0], -1)))
        print("P_tilde_dash_yc")
        print(P_tilde_dash_yc.shape)

        xPyc = [F.exp(F.flatten(F.matmul(pyc, F.transpose(x)))) for pyc, x in zip(F.split_axis(P_tilde_dash_yc, P_tilde_dash_yc.shape[0], axis=0), tilde_xs)]
        print("xPyc")
        print([i.shape for i in xPyc])

        print("check")
        print([F.expand_dims(F.expand_dims(x, axis=0), axis=3).shape for x in tilde_xs])


        print("pad_size")
        print(self.pad_size_former)
        print(self.pad_size_latter)
        
        padded_xs = [F.concat((F.concat((F.broadcast_to(x[0], (self.pad_size_former, self.H_hidden_size)), x), axis=0), F.broadcast_to(x[-1], (self.pad_size_latter, self.H_hidden_size))), axis=0) for x in tilde_xs]

        print("tilde_xs")
        print([i.shape for i in tilde_xs])
        print("padded_xs")
        print([i.shape for i in padded_xs])

        print()
        print(padded_xs[0])
        print()
        
        bar_xs = [F.average_pooling_2d(F.expand_dims(F.expand_dims(x, axis=0), axis=1), ksize=(self.Q_smoothing_window, 1), stride=(1, 1), pad=0) for x in padded_xs]
        print("bar_xs")
        print([i.shape for i in bar_xs])
        bar_xs = [F.squeeze(x, axis=(0, 1)) for x in bar_xs]
        print("tilde_xs")
        print([i.shape for i in tilde_xs])
        print("bar_xs")
        print([i.shape for i in bar_xs])
        
        enc = F.concat([F.matmul(F.expand_dims(p, axis=0), bar_x) for p, bar_x in zip(xPyc, bar_xs)], axis=0)
        print("enc")
        print(enc.shape)
        print([i.shape for i in enc])
        
        ### NLM ###
        tilde_yc = self.E(yc)
        print("tilde_yc")
        print(tilde_yc.shape)

        h = self.activate(self.U(tilde_yc))
        print("h")
        print(h.shape)


        ### Integrate ###
        y = self.V(h) + self.W(enc)
        print("y")
        print(y.shape)
        
        if self.return_enc:
            pass
        
        return y
