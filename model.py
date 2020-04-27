import torch
import torch.nn as nn
import torch.nn.functional as F

class Anomaly_Classifier(nn.Module):
    def __init__(self, input_size, num_classes):
        super(Anomaly_Classifier, self).__init__()

        self.conv = nn.Conv1d(in_channels=input_size, out_channels=32, kernel_size=5, stride=1)

        self.conv_pad = nn.Conv1d(in_channels=32, out_channels=32, kernel_size=5, stride=1, padding=2)
        self.drop_50 = nn.Dropout(p=0.5)

        self.maxpool = nn.MaxPool1d(kernel_size=5, stride=2)

        self.dense1 = nn.Linear(32 * 8, 32)
        self.dense2 = nn.Linear(32, 32)

        self.dense_final = nn.Linear(32, num_classes)
        self.softmax = nn.LogSoftmax(dim=1)
        # self.softmax = nn.Softmax

    def forward(self, x):
        residual = self.conv(x)

        # block1
        x = F.relu(self.conv_pad(residual))
        x = self.conv_pad(x)
        x += residual
        x = F.relu(x)
        residual = self.maxpool(x)  # [512 32 90]

        # block2
        x = F.relu(self.conv_pad(residual))
        x = self.conv_pad(x)
        x += residual
        x = F.relu(x)
        residual = self.maxpool(x)  # [512 32 43]

        # block3
        x = F.relu(self.conv_pad(residual))
        x = self.conv_pad(x)
        x += residual
        x = F.relu(x)
        residual = self.maxpool(x)  # [512 32 20]

        # block4
        x = F.relu(self.conv_pad(residual))
        x = self.conv_pad(x)
        x += residual
        x = F.relu(x)
        x = self.maxpool(x)  # [512 32 8]

        # MLP
        x = x.view(-1, 32 * 8)  # Reshape (current_dim, 32*2)
        x = F.relu(self.dense1(x))
        # x = self.drop_60(x)
        x = self.dense2(x)
        x = self.dense_final(x)
        x = self.softmax(x)  # actually logsoftmax, should all minus values.
        return x

##################MAIN#########################
if __name__ == '__main__':
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(device)

    input_tensor = torch.autograd.Variable(torch.rand(1,1,180)).cuda()
    model = Anomaly_Classifier(input_size= 1, num_classes= 5).cuda()
    # output = model(input_tensor)
    output = model(input_tensor)
    print(output)

    # print('Model Architecture Init\n')
    # print("OPTIMIZER = optim.Adam(anom_classifier.parameters(),lr = 0.001) \n ")

