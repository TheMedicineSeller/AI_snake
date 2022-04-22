import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
class Linear_QNet(nn.Module):
    # Parameters depecting the no of nodes in each layer of the NN
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)
    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr = self.lr)
        self.criterion = nn.MSELoss()  # Mean square error
    def train_step(self, state, action, reward, next_state, over):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        if len(state.shape) == 1:
            # When the input array is just 1D (one single train step call)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            over = (over,)
        # Predicted Q value with current state
        pred = self.model(state)
        target = pred.clone()
        # as the states, rewards etc. are all zipped together into a tuple
        for idx in range(len(over)):
            Q_new = reward[idx]
            if not over[idx]:
                # Q_new = reward + discount*Q_future
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            target[idx][torch.argmax(action[idx]).item()] = Q_new
        # Call to empty the gradient
        self.optimizer.zero_grad()
        # Calculating mse b/w q, qnext
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()
        

