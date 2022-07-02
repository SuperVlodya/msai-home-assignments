#!/usr/bin/env python
# coding: utf-8

# In[2]:


import yaml


class Config:
    def __init__(self):
        with open('config.yaml', 'r') as file:
            self._config = yaml.load(file, Loader=yaml.FullLoader)
        # print(self._config['requests'][0]['method'])

    @property
    def config(self):
        return self._config

    def __call__(self):
        return self._config

    @property
    def requests(self) -> list:
        return self._config['requests']

    @property
    def stages(self) -> list:
        return self._config['STAGES']


# In[ ]:





# In[ ]:




