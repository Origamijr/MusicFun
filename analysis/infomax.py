import numpy as np
import librosa

def infomax(X, lr=2e-5):
    n = X.shape[0]
    W = [np.random.rand(n,n) - 0.5]
    I = np.identity(4)
    dist = 100
    v = np.zeros((4,4))
    
    print(W[0])
    while dist > 1e-4:
        Y = W[len(W) - 1] @ X
        v = 0.9 * v + lr * (I - np.tanh(Y) @ Y.T) @ W[len(W) - 1]
        w = W[len(W) - 1] + v
        #print(lr*(I - np.tanh(Y) @ Y.T) @ W[len(W) - 1])
        W.append(w)
        dist = np.linalg.norm(W[len(W) - 1] - W[len(W) - 2])
        #print(dist)

    return W[len(W) - 1] @ X, W[len(W) - 1]

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
    s1, sr = librosa.load("data\\DSD100subset\\Sources\\Test\\005 - Angela Thomas Wade - Milk Cow Blues\\bass.wav")
    s2, sr = librosa.load("data\\DSD100subset\\Sources\\Test\\005 - Angela Thomas Wade - Milk Cow Blues\\drums.wav")
    s3, sr = librosa.load("data\\DSD100subset\\Sources\\Test\\005 - Angela Thomas Wade - Milk Cow Blues\\other.wav")
    s4, sr = librosa.load("data\\DSD100subset\\Sources\\Test\\005 - Angela Thomas Wade - Milk Cow Blues\\vocals.wav")
    S = np.vstack((s1, s2, s3, s4))
    A = np.random.rand(4,4) / 2
    X = A @ S
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_mix1.wav", X[0,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_mix2.wav", X[1,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_mix3.wav", X[2,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_mix4.wav", X[3,:].flatten(), sr, norm=True)

    Y, W = infomax(X)
    print(W - np.linalg.inv(A))
    #print(Y)

    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix1.wav", Y[0,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix2.wav", Y[1,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix3.wav", Y[2,:].flatten(), sr, norm=True)
    librosa.output.write_wav("data\\DSD100subset\\Out\\05_unmix4.wav", Y[3,:].flatten(), sr, norm=True)



