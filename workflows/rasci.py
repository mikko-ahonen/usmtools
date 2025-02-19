class RASCI():
    REGEX = '^R?A?S?C?I?$'

    def __init__(self, types='', R=False, A=False, S=False, C=False, I=False):
        self.R = R
        self.A = A
        self.S = S
        self.C = C
        self.I = I
        self.add_types(types)

    def add_types(self, rtypes):
        for rtype in rtypes:
            if rtype == 'R':
                self.R = True
            elif rtype == 'A':
                self.A = True
            elif rtype == 'S':
                self.S = True
            elif rtype == 'C':
                self.C = True
            elif rtype == 'I':
                self.I = True
            else:
                raise ValueError("Only R, A, S, C and I are allowed as responsibility types")
        return self

    def remove_types(self, rtypes):
        for rtype in rtypes:
            if rtype == 'R':
                self.R = False
            elif rtype == 'A':
                self.A = False
            elif rtype == 'S':
                self.S = False
            elif rtype == 'C':
                self.C = False
            elif rtype == 'I':
                self.I = False
            else:
                raise ValueError("Only R, A, S, C and I are allowed as responsibility types")
        return self
            
    def get_types(self):
        retval = ''
        if self.R:
            retval += 'R'
        if self.A:
            retval += 'A'
        if self.S:
            retval += 'S'
        if self.C:
            retval += 'C'
        if self.I:
            retval += 'I'
        return retval
        
