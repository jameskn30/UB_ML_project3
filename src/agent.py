import gymnasium as gym
from gymnasium import spaces
import numpy as np
from tqdm import tqdm 
import random
import os
import json
import uuid

class QLearningAgent():
    def __init__(self, env, **kwargs: dict) -> None:
        self.n_training_eps = int(self._get(kwargs, "n_training_eps", 10000))
        self.n_eval_eps = int(self._get(kwargs, "n_eval_eps", 100))
        self.max_steps = int(self._get(kwargs, "max_steps", 99))
        self.learning_rate = float(self._get(kwargs, "learning_rate", 0.001))
        self.max_epsilon = float(self._get(kwargs, "max_epsilon", 1.0))
        self.min_epsilon = float(self._get(kwargs, "min_epsilon", 0.005))
        self.decay_rate = float(self._get(kwargs, "decay_rate", 0.0005))
        self.gamma = float(self._get(kwargs, "gamma", 0.95))
        self.env = env
        self._reset_qtable()
    
    def _reset_qtable(self):
        self.qtable = self._init_qtable(self.env.observation_space.n, self.env.action_space.n)

    def __str__(self):
        print("=" * 20)
        print(f"Q-TABLE, shape = {self.qtable.shape}")
        print("=" * 20)
        print(self.qtable)
        print("=" * 20)
        print("PARAMS")
        print("=" * 20)
        print(f'n_training_eps = {self.n_training_eps}')
        print(f'n_eval_eps = {self.n_eval_eps}')
        print(f'max_steps = {self.max_steps}')
        print(f'learning_rate = {self.learning_rate}')
        print(f'max_epsilon = {self.max_epsilon}')
        print(f'min_epsilon = {self.min_epsilon}')
        print(f'decay rate = {self.decay_rate}')
        print(f'gamma = {self.gamma}')
        print(f'env = {self.env}')
        return ''

    def _get(self, dict, key, default):
        return dict[key] if key in dict else default

    def _init_qtable(self, state_space,action_space):
        qtable = np.zeros((state_space, action_space))
        return qtable
    
    def _epsilon_greedy_policy(self, state, epsilon):
        random_init = random.uniform(-1,1)
        if random_init > epsilon:
            action = np.argmax(self.qtable[state])
        else:
            action = self.env.action_space.sample()
        return action
    
    def train(self):
        loop = tqdm(list(range(self.n_training_eps)))
        #reset qtable
        self._reset_qtable()

        print("=" * 20)
        print("QLEARNING TRAINING")
        print("=" * 20)
        reached_goal_count = 0
        termination_count = 0

        for ep in loop:
            epsilon = self.min_epsilon + (self.max_epsilon - self.min_epsilon) * np.exp(-self.decay_rate * ep)
            state = self.env.reset()
            done = False

            for step in range(self.max_steps):
                action = self._epsilon_greedy_policy(state, epsilon)
                new_state, reward, done, terminated, info = self.env.step(action)

                self.qtable[state][action] = self.qtable[state][action] + \
                    self.learning_rate * (reward  + self.gamma * \
                                          np.max(self.qtable[new_state]) - self.qtable[state][action])
                
                state = new_state

                if terminated:
                    termination_count += 1
                    break
                elif done:
                    reached_goal_count += 1
                    break
            
            loop.set_description(f"ep = {ep}, eposilon = {epsilon:.2f}, reached goals = {reached_goal_count}, terminated = {termination_count}")
    
    def get_action(self, state):
        return np.argmax(self.qtable[state])
       
    def save(self, path = 'qtable.npy'):
        with open(path, 'wb') as file:
            np.save(file, self.qtable)

    def load(self, path = 'qtable.npy'):
        with open(path, 'rb') as file:
            self.qtable = np.load(file)
   
    def save_attempt(self, id = None):
        if id == None:
            id = str(uuid.uuid4()).split('-')[0]
        attemp_dir = f'./attempts/{id}'
        map = self.env.map
        qtable = self.qtable

        if os.path.exists(attemp_dir) == False:
            os.path.join(attemp_dir, f'attemp_{1}')
            os.makedirs(attemp_dir)
        map_path = os.path.join(attemp_dir,'map.json')
        with open(map_path, 'w') as mapfile:
            json.dump(map, mapfile)
        
        qtable_path = os.path.join(attemp_dir,'qtable.npy')
        with open(qtable_path, 'wb') as qtablefile:
            np.save(qtablefile, qtable)
        return id

    def load_attempt(self, id):
        attemp_dir = f'./attempts/{id}'
        if os.path.exists(attemp_dir):
            map_path = os.path.join(attemp_dir,'map.json')
            with open(map_path, 'rb') as mapfile:
                map = json.load(mapfile)
                self.env.map = map
            
            qtable_path = os.path.join(attemp_dir,'qtable.npy')
            with open(qtable_path, 'rb') as qtablefile:
                qtable = np.load(qtablefile)
                self.qtable = qtable
            
            return map, qtable
        else:
            raise FileNotFoundError(f"{attemp_dir} directory not found") 


class SarsaAgent():

    def __init__(self, env, **kwargs: dict) -> None:
        self.n_training_eps = int(self._get(kwargs, "n_training_eps", 10000))
        self.n_eval_eps = int(self._get(kwargs, "n_eval_eps", 100))
        self.max_steps = int(self._get(kwargs, "max_steps", 99))
        self.learning_rate = float(self._get(kwargs, "learning_rate", 0.001))
        self.max_epsilon = float(self._get(kwargs, "max_epsilon", 1.0))
        self.min_epsilon = float(self._get(kwargs, "min_epsilon", 0.005))
        self.decay_rate = float(self._get(kwargs, "decay_rate", 0.0005))
        self.gamma = float(self._get(kwargs, "gamma", 0.95))
        self.env = env
        self._reset_qtable()
    
    def _reset_qtable(self):
        self.qtable = self._init_qtable(self.env.observation_space.n, self.env.action_space.n)

    def __str__(self):
        print("=" * 20)
        print(f"Q-TABLE, shape = {self.qtable.shape}")
        print("=" * 20)
        print(self.qtable)
        print("=" * 20)
        print("PARAMS")
        print("=" * 20)
        print(f'n_training_eps = {self.n_training_eps}')
        print(f'n_eval_eps = {self.n_eval_eps}')
        print(f'max_steps = {self.max_steps}')
        print(f'learning_rate = {self.learning_rate}')
        print(f'max_epsilon = {self.max_epsilon}')
        print(f'min_epsilon = {self.min_epsilon}')
        print(f'decay rate = {self.decay_rate}')
        print(f'gamma = {self.gamma}')
        print(f'env = {self.env}')
        return ''

    def _get(self, dict, key, default):
        return dict[key] if key in dict else default

    def _init_qtable(self, state_space,action_space):
        qtable = np.zeros((state_space, action_space))
        return qtable
    
    def _epsilon_greedy_policy(self, state, epsilon):
        random_init = random.uniform(-1,1)
        if random_init > epsilon:
            action = np.argmax(self.qtable[state])
        else:
            action = self.env.action_space.sample()
        return action
    
    def train(self):
        loop = tqdm(list(range(self.n_training_eps)))
        #reset qtable
        self._reset_qtable()

        print("=" * 20)
        print("SARSA TRAINING")
        print("=" * 20)
        reached_goal_count = 0
        termination_count = 0

        for ep in loop:
            epsilon = self.min_epsilon + (self.max_epsilon - self.min_epsilon) * np.exp(-self.decay_rate * ep)
            state = self.env.reset()
            done = False

            for step in range(self.max_steps):
                action = self._epsilon_greedy_policy(state, epsilon)
                new_state, reward, done, terminated, info = self.env.step(action)
                next_action = self._epsilon_greedy_policy(new_state,epsilon)

                #SARSA formua 
                self.qtable[state][action] = self.qtable[state][action] + \
                    self.learning_rate * (reward  + self.gamma * \
                    self.qtable[new_state][next_action] - self.qtable[state][action])
                
                state = new_state

                if terminated:
                    termination_count += 1
                    break
                elif done:
                    reached_goal_count += 1
                    break
            
            loop.set_description(f"ep = {ep}, eposilon = {epsilon:.2f}, reached goals = {reached_goal_count}, terminated = {termination_count}")
    
    def get_action(self, state):
        return np.argmax(self.qtable[state])
    
    def save(self, path = 'qtable.npy'):
        with open(path, 'wb') as file:
            np.save(file, self.qtable)

    def load(self, path = 'qtable.npy'):
        with open(path, 'rb') as file:
            self.qtable = np.load(file)

    def save_attempt(self, id = None):
        if id == None:
            id = str(uuid.uuid4()).split('-')[0]
        attemp_dir = f'./attempts/{id}'
        map = self.env.map
        qtable = self.qtable

        if os.path.exists(attemp_dir) == False:
            os.path.join(attemp_dir, f'attemp_{1}')
            os.makedirs(attemp_dir)
        map_path = os.path.join(attemp_dir,'map.json')
        with open(map_path, 'w') as mapfile:
            json.dump(map, mapfile)
        
        qtable_path = os.path.join(attemp_dir,'qtable.npy')
        with open(qtable_path, 'wb') as qtablefile:
            np.save(qtablefile, qtable)
        return id

    def load_attempt(self, id):
        attemp_dir = f'./attempts/{id}'
        if os.path.exists(attemp_dir):
            map_path = os.path.join(attemp_dir,'map.json')
            with open(map_path, 'rb') as mapfile:
                map = json.load(mapfile)
            
            qtable_path = os.path.join(attemp_dir,'qtable.npy')
            with open(qtable_path, 'rb') as qtablefile:
                qtable = np.load(qtablefile)
            
            return map, qtable
        else:
            raise FileNotFoundError(f"{attemp_dir} directory not found")