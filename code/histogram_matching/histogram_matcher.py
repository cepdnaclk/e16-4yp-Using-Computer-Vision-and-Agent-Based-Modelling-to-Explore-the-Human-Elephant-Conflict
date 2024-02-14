import cv2
from skimage import exposure
import matplotlib.pyplot as plt

source = '6.png'
ref = cv2.cvtColor(cv2.imread('ref.png'), cv2.COLOR_BGR2RGB)
src = cv2.cvtColor(cv2.imread(source), cv2.COLOR_BGR2RGB)

multi = True if src.shape[-1] > 1 else False

matched = exposure.match_histograms(src, ref, multichannel=multi)

plt.rc('figure', figsize=(15, 5))

plt.subplot(1,3,1), plt.title('source'), plt.imshow(src)
plt.xticks([]), plt.yticks([])
plt.subplot(1,3,2), plt.title('reference'), plt.imshow(ref)
plt.xticks([]), plt.yticks([])
plt.subplot(1,3,3), plt.title('result'), plt.imshow(matched)
plt.xticks([]), plt.yticks([])



plt.savefig(f'plots/{source.split(".")[0]}_plot.png')
# plt.show()

cv2.imwrite(f'matched/{source.split(".")[0]}_matched.png', matched)

# cv2.waitKey(0)