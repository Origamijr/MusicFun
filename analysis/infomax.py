import numpy as np
import librosa

def infomax(X, lr=1e-6, mix=None):
    n = X.shape[0]
    W = np.random.rand(n,n) - 0.5
    I = np.identity(4)
    dist = 100
    v = np.zeros((4,4))
    
    print(W[0])
    while dist > 1e-4:
        Y = W @ X
        v = 0.9 * v + lr * (I - np.tanh(Y) @ Y.T) @ W
        Wn = W + v
        #print(lr*(I - np.tanh(Y) @ Y.T) @ W[len(W) - 1])
        #W.append(w)
        dist = np.linalg.norm(W - Wn)
        W = Wn
        if mix is not None:
            print(W @ mix)

    return W @ X, W

def whitening(X):
    
    X -= np.reshape(np.mean(X, axis=0), (1, -1))
    U, d, V = np.linalg.svd(np.cov(X), full_matrices=False)
    return np.linalg.inv(np.sqrt(np.diag(d[:X.shape[0]]))) @ U[:,:X.shape[0]].T @ X
    """
    X = X.T
    d, m = X.shape
    mean = np.mean(X, axis=1)[:, np.newaxis]
    A = X - mean
    eig_vals, eig_vecs = np.linalg.eig((A.T @ A) / m)
    AAT_eigenvecs = A @ eig_vecs
    largest_i = eig_vals.argsort()[::-1]
    sorted_eigenvecs = AAT_eigenvecs[:, largest_i][:,:m]
    sorted_eigenvecs = sorted_eigenvecs / np.linalg.norm(sorted_eigenvecs, axis=0)[np.newaxis, :]
    return sorted_eigenvecs.T"""

if __name__ == "__main__":
    """
    mix1, sr = librosa.load("data\\DSD100subset\\MultiMix\\05_mix1.wav")
    mix2, _ = librosa.load("data\\DSD100subset\\MultiMix\\05_mix2.wav")
    mix3, _ = librosa.load("data\\DSD100subset\\MultiMix\\05_mix3.wav")
    mix4, _ = librosa.load("data\\DSD100subset\\MultiMix\\05_mix4.wav")
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_samp.wav", mix1, sr)
    X = np.vstack((mix1, mix2, mix3, mix4))

    Y, W = infomax(X)
    print(W)
    print(Y)

    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix1.wav", Y[0,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix2.wav", Y[1,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix3.wav", Y[2,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix4.wav", Y[3,:].flatten(), sr, norm=True)
    """
    source_path = "data\\DSD100subset\\Sources\\Dev\\081 - Patrick Talbot - Set Me Free\\"
    s1, sr = librosa.load(source_path + "bass.wav")
    s2, sr = librosa.load(source_path + "drums.wav")
    s3, sr = librosa.load(source_path + "other.wav")
    s4, sr = librosa.load(source_path + "vocals.wav")
    S = np.vstack((s1, s2, s3, s4))
    A = np.random.rand(4,4) / 4 + 0.25
    X = A @ S
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_source1.wav", s1, sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_source2.wav", s2, sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_source3.wav", s3, sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_source4.wav", s4, sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_mix1.wav", X[0,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_mix2.wav", X[1,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_mix3.wav", X[2,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_mix4.wav", X[3,:].flatten(), sr, norm=True)

    print(X)
    X = whitening(X)
    print(X)
    Y, W = infomax(X, mix=A)
    print(W @ A)
    #print(Y)

    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix1.wav", Y[0,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix2.wav", Y[1,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix3.wav", Y[2,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix4.wav", Y[3,:].flatten(), sr, norm=True)



