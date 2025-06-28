from ai.Model import Net
import torch
import cv2
import numpy as np

net = Net()
net.load_state_dict(torch.load("model.pth", weights_only=True))

file = f"frame.png"
image = cv2.imread(file)
inputs = image[:32, :32]
inputs = (inputs / 128) - 1
inputs = inputs.transpose(2, 0, 1)
inputs = torch.tensor(np.array([inputs], dtype=np.float32))

outputs = net.forward(inputs)
print(outputs)
