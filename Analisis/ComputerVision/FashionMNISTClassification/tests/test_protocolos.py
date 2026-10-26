from pathlib import Path
import sys
import unittest
import tempfile
import gzip
import struct
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from fashion_mnist_classification.data import read_idx, partition, features, fingerprints


class ProtocolosTest(unittest.TestCase):
    def test_idx_truncado_y_etiquetas_invalidas_se_rechazan(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            path=Path(folder)/'test.gz'
            for payload in (struct.pack('>IIII',2051,2,28,28)+bytes(784),struct.pack('>II',2049,1)+bytes([10])):
                with gzip.open(path,'wb') as f:f.write(payload)
                with self.assertRaises(ValueError):read_idx(path)

    def test_preparacion_evitar_solapamientos_por_contenido(self):
        rng=np.random.default_rng(4)
        images=rng.integers(0,256,(200,28,28),dtype=np.uint8)
        labels=np.repeat(np.arange(10),20)
        # Repetición y grupo ambiguo se retiran del desarrollo; test permanece externo.
        x=np.concatenate([images,images[:1],images[1:2]])
        y=np.concatenate([labels,[labels[0]],[9]])
        test=images[2:3].copy()
        train,valid,info=partition(x,y,test,{'seed':42,'valid_fraction':0.2,'train_limit':100,'valid_limit':30})
        a,b,t=set(fingerprints(x[train])),set(fingerprints(x[valid])),set(fingerprints(test))
        self.assertFalse(a&b);self.assertFalse((a|b)&t)
        self.assertEqual(info['grupos_ambiguos'],1)
        self.assertEqual(len(train),100);self.assertEqual(len(valid),30)
        self.assertTrue(all(len(np.unique(y[ids]))==10 for ids in (train,valid)))

    def test_normalizacion_constante_sin_mutar_imagen(self):
        image=np.full((1,28,28),255,dtype=np.uint8)
        x=features(image)
        self.assertEqual(x.shape,(1,784));self.assertEqual(x.dtype,np.float32)
        self.assertTrue(np.all(x==1));self.assertTrue(np.all(image==255))

if __name__=='__main__':unittest.main()
