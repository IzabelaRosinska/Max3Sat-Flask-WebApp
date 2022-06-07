class Problem:
    '''Class Problem allows to read optimization problem from a .txt file.
    Stores information about the optimization problem to solve.
    Gives back information about the problem and quality of solution.'''

    def __init__(self, number_of_variables_in_clause, filepath):
        '''Object of Problem stores information about the structure of the file with problem.
        As arguments takes:
        number_of_variables_in_clause - tells from how many variables the clause should be made of and
        filepath - filepath to .txt file with problem to solve'''
        
        self._number_of_clauses = 0
        self._number_of_variables = 0
        self._number_of_variables_in_clause = number_of_variables_in_clause
        self._filepath = filepath
        self._clauses = []
        self._signs = []
        self._variables_with_their_clauses = []

    @property
    def number_of_variables(self):
        '''Returns number of variables present in the Problem object.'''
        return self._number_of_variables

    @property
    def number_of_clauses(self):
        '''Returns number of clauses present in the Problem object.'''
        return self._number_of_clauses
        
    def check_number_of_clauses(self):
        '''Counts number of clauses present in the Problem file and stores information in variable self._number_of_clauses.'''
        
        with open(self._filepath, 'r', encoding='utf-8') as file:
            for _ in file:
                self._number_of_clauses += 1
            
    def assign_clauses_to_variables(self):
        '''Assigns clauses containing given variable to variable's list of clauses.'''
        
        for _ in range(self.number_of_variables):
            self._variables_with_their_clauses.append([])

        for i in range(self._number_of_clauses):
            for j in range(self._number_of_variables_in_clause):
                self._variables_with_their_clauses[self._clauses[i][j]].append(i)

    def check_clauses_with_variable(self, variable, genotype):
        '''Returns the Integer value telling how many clauses containing given variable are fullfiled.
        As arguments takes:
        variable - index of variable present in the problem structure
        genotype - genotype coding (with 0 and 1) values of all variables present in the problem structure'''
        
        number_of_fulfilled_clauses = 0

        for clause in self._variables_with_their_clauses[variable]:
            if self.evaluate_single_clause(clause, genotype):
                number_of_fulfilled_clauses += 1

        return number_of_fulfilled_clauses

    def compute(self, genotype):
        '''Returns the Integer value telling how many clauses from Problem file are fullfiled.
        As arguments takes:
        genotype - genotype coding (with 0 and 1) values of all variables present in the problem structure'''
        
        number_of_fulfilled_clauses = 0

        for clause in range(self._number_of_clauses):
            if self.evaluate_single_clause(clause, genotype):
                number_of_fulfilled_clauses += 1

        return number_of_fulfilled_clauses

    def evaluate(self, genotype):
        '''Returns the Real value telling the ratio of fulfilled clauses to all clauses from Problem file.
        As arguments takes:
        genotype - genotype coding (with 0 and 1) values of all variables present in the problem structure'''

        number_of_fulfilled_clauses = self.compute(genotype)
        return number_of_fulfilled_clauses / self._number_of_clauses

    def evaluate_single_clause(self, which_clause, genotype):
        '''Returns True if given clause is fulfilled and False otherwise.
        As arguments takes:
        which_clause - index of clause present in the problem
        genotype - genotype coding (with 0 and 1) values of all variables present in the problem structure'''

        for variable in range(self._number_of_variables_in_clause):
            if self._signs[which_clause][variable]:
                if genotype[self._clauses[which_clause][variable]] == 1:
                    return True
            else:
                if genotype[self._clauses[which_clause][variable]] == 0:
                    return True

        return False
    
    def load(self):
        '''Reads problem structure from file. Returns True if file was properly formatted and False otherwise.'''
        
        self.check_number_of_clauses()

        if self.number_of_clauses == 0:
            return False
        
        for _ in range(self._number_of_clauses):
            self._clauses.append([])
            self._signs.append([])
        
        clause = 0
        
        with open(self._filepath, 'r', encoding='utf-8') as file:
            for line in file:
                variables_temporary = line.split()
                check_number_of_variables = 0
                
                for string_to_analyze in variables_temporary:
                    if string_to_analyze == '(' or string_to_analyze == ')':
                        pass
                    else:
                        try:
                            variable = int(string_to_analyze)
                        except:
                            return False

                        if string_to_analyze[0] != '-':
                            self._signs[clause].append(True)
                        else:
                            variable = (-1) * variable
                            self._signs[clause].append(False)

                        self._clauses[clause].append(variable)
                        
                        if variable > self.number_of_variables:
                            self._number_of_variables = variable

                        check_number_of_variables += 1

                if check_number_of_variables != self._number_of_variables_in_clause:
                    return False

                clause += 1

            self._number_of_variables += 1
            self.assign_clauses_to_variables()

            return True

    def print_clauses(self):
        '''Prints structure of the Problem read from the file.'''
        
        print("Number of clauses:", self._number_of_clauses)
        print("\nNumber of variables:", self.number_of_variables)
        result_to_show = ""
        
        for i in range(self._number_of_clauses):
            for j in range(self._number_of_variables_in_clause):
                if self._signs[i][j]:
                    result_to_show += str(self._clauses[i][j]) + " "
                else:
                    result_to_show += "-" + str(self._clauses[i][j]) + " "
            result_to_show += "\n"

        print(result_to_show)