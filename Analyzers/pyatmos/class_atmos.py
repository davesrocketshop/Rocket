class ATMOS(object):
    '''
    class ATMOS
    - attributes:
        - self defined

    - methods:
        - None
    '''
    def __init__(self,info):
        self.info = info

        for key in info.keys():
            setattr(self, key, info[key])  
   
    def __repr__(self):
        return 'Instance of class ATMOS' 