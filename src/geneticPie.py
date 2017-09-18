import random
import copy

class GenBuffer(object):

    def __init__(self, gen = None, new_instace = None, gen_class = None):
        if  gen:
            self.new_instace = gen.new_instace
            self.gen_class = gen.__class__
        elif new_instace and gen_class:
            self.new_instace = new_instace
            self.gen_class = gen_class
        else:
            raise ValueError("Tehere is not enough param")


class Gen(object):
    """Public Class
    Representation of an changeble information for an possible responce."""

    def __init__(self, mutation_list = [], validation_list = []):
        """Public method
        Initiate Gen with mutation_list ans validation_list."""
        self.mutation_list = mutation_list
        self.validation_list = validation_list

    def create_buffer(self):
        return GenBuffer(gen = self)

    def all_subclass(self, lst, cls):
        """Protected method
        verify if all elements in iterable lst extends cls"""
        for x in lst:
            if not issubclass(x.__class__, cls): return False
        return True

    @property
    def validation_list(self): return self.__validation_list

    @validation_list.setter
    def validation_list(self, vl):
        if (not self.all_subclass(vl, Validation)):
            raise TypeError('elements in validation_list must extend Validation')
        self.__validation_list = vl

    @property
    def mutation_list(self): return self.__mutation_list

    @mutation_list.setter
    def mutation_list(self, ml):
        if (not self.all_subclass(ml, Mutation)):
            raise TypeError('elements in mutation_list must extend Mutation')
        self.__mutation_list = ml

    def mutate(self):
        """Public Method
        If there is something in mutation list, execute self.validate
        and in on in eatch five times, takes one of mutation_list (randomly) and execute it.
        If there is not any Mutation avaliable, nothing happens."""
        if self.mutation_list and not random.randint(0,4):
            random.choice(self.mutation_list).mutate(self)

    def validade(self):
        """Public Method
        Execute every Validation in validation_list."""
        for val in self.validation_list:
            val.validate(self)

    def new_instace(self):
        return copy.deepcopy(self)

class Mutation(object):
    """Public Class
    Executable Mutation for a Gen, must recieve the method 'mutate' to execute when initiated
    Mutate recieve self and the gen, it must change a something in gen, in order to change its value"""

    def __init__(self, mutate = None):
        """Public method
        Initiate Mutation with mutate param"""
        self.mutate = mutate if mutate else param['mutate']

    def mutate(self, gen):
        """Public Method
        change something in Gen in order to change its value.
        Must be overrided."""
        raise NotImplementedError()

class Validation(object):
    """Public Class
    Executable Validation for a Gen, must recieve the method 'validate' to execute when initiated.
    validate recieve self and the Gen, it must change a something in Gen,
    in order to make it have a valid value."""
    
    def __init__(self, validate = None):
        """Public method
        Initiate Validation with validate param"""
        self.validate = validate if validate else param['validate']

    def validate(self, gen):
        """Public Method
        validate gen in order to make it have an valid value.
        Must be overrided."""
        raise NotImplementedError()



class ValuableGen(Gen):
    """Public Class
    Gen that has a value."""    

    def __init__(self, value = None, mutation_list = [], validation_list = []):
        """Public method
        Initiate ValuableGen with value, mutation_list ans validation_list."""
        self.value = value
        Gen.__init__(self, mutation_list = mutation_list, validation_list = validation_list)

        @property
        def value(self): return self.__value
        @value.setter
        def value(self, v): self.__value = v

    def __str__(self):
        return str(self.value);

class RunnableGen(Gen):
    """Public Class
    Gen that implements an run method."""

    def __init__(self, names = [], individual = None, req_gens = {},mutation_list = [], validation_list = []):
        """Public method
        Iinitiate RunnableGen with names, individual, req_gen, mutation_list and validation_list."""
        self.names = names if names else [k for k in req_gens.keys()]
        self.individual = individual
        self.req_gens = req_gens
        Gen.__init__(self, mutation_list = mutation_list, validation_list = validation_list)

        @property
        def req_gens(self): return self._req_gens

        @req_gens.setter
        def req_gen(self, rg):
            if (not all_subclass(rg.values(), Gen)):
                raise TypeError('values in req_gens must extend Gen')
            self._req_gens = rg

    def run(self, param):
        """Public Method Execute some task, returnnig or not.
        Must be overrided."""
        raise NotImplementedError()

class Individual(object):
    """Public Class
    Representation of an possible response."""
    
    def __init__(self, base_gen_dict):
        self.gens = base_gen_dict
        requier_list = [requier for requier in base_gen_dict.values()]
        while requier_list:
            requier = requier_list.pop(-1)
            if not issubclass(requier.__class__, RunnableGen): continue
            requier.individual = self
            req_dict = requier.req_gens
            for name, buf in req_dict.items():
                new_name = name
                if name in self.gens:
                    if issubclass(buf.gen_class, self.gens[name].__class__):continue
                    i = 0
                    new_name = name+'_'+str(i)
                    while new_name in self.gens: name+'_'+str(i)
                    if name != new_name:
                        requier.req_gens[name] = requier.req_gens.pop(name)
                        requier.names[requier.names.index(name)] = new_name
                instance = buf.new_instace()
                requier_list.append(instance)
                self.gens[new_name] = instance

    def calculate_fitness(self, param):
        """Public Method
        Calculate and return an numerical indicator of Individual addaptability.
        Zero is te perfect response, representing that the individual is the most optimizated response.
        Must be overrided."""
        raise NotImplementedError()

    def crossover(self, partner):
        """Public Method
        Return a new instance of the Indiviual class, based on its gens end partner gens."""
        if not issubclass(partner.__class__, Individual):
            raise TypeError("partner must be an Individual")

        gen_name_list = [*self.gens.keys(), *partner.gens.keys()]
        gen_dict = {}
        for gen_name in gen_name_list:
            if gen_name not in self.gens:
                gen_dict[gen_name] = partner.gens[gen_name]
            elif gen_name not in partner.gens:
                gen_dict[gen_name] = self.gens[gen_name]
            else:
                random.choice((self.gens[gen_name], partner.gens[gen_name]))

        new_ind = self.__class__({k : v.new_instace() for k,v in gen_dict.items()})
        for gen in new_ind.gens.values():
            gen.mutate()
            gen.validade()
        return new_ind

    def new_instace(self):
        """Public Method
        Returns a new instance of the object's class."""
        return copy.deepcopy(self)

class Simulation(object):
    """Public Class
    Simulation of the the population and its processes"""

    def __init__(self, population = None):
        if population:
            self.population = population
        else:
            self.population = []

        self.ind_params = []

    def eliminate(self, list_selector = None, single_selector = None):
        """Public Method
        Sort population using the last value passad to this object's attribute sort_by_fitness.
        If list_selector is received, the new population is the return of it.
        list_selector must be a function that receive the current population as paramether
        Else, if single_selector is received, the new population will be the part of 
        the current that being passed to single_selector makes it return true"""
        self.sort_by_fitness()
        before = len(self.population)
        if (list_selector):
            self.population = list_selector(self.population)
        elif single_selector:
            self.population = [ind for ind in self.population if single_selector(ind)]
        else:
            self.population = self.population[0:int((len(self.population)+1)/2)]

        return before-len(self.population)

    def sort_by_fitness(self, param = None):

        if param and not param in self.ind_params:
            self.ind_params.append(param)

        def key(ind): return ind.calculate_fitness(self.ind_params[-1])

        self.population.sort(key = key)
        return self

class Default():
    """Public Static Class.
    Default owns Default Gen, Mutation and Validation implementations."""

    class Mut():
        """Private Class"""
        def add_1(gen):
            gen.value += 1
        def add_10(gen):
            gen.value += 10 
        def add_100(gen):
            gen.value += 100
        def sub_1(gen):
            gen.value -= 1
        def sub_10(gen):
            gen.value -= 10
        def sub_100(gen):
            gen.value -= 100
        def mul_1(gen):
            gen.value *= 1
        def mul_10(gen):
            gen.value *= 10
        def mul_100(gen):
            gen.value *= 100
        def div_1(gen):
            gen.value /= 1
        def div_10(gen):
            gen.value /= 10
        def div_100(gen):
            gen.value /= 100
        def add_05(gen):
            gen.value += 0.5
        def add_01(gen):
            gen.value += 0.1
        def add_001(gen):
            gen.value += 0.01
        def sub_05(gen):
            gen.value -= 0.5
        def sub_01(gen):
            gen.value -= 0.1
        def sub_001(gen):
            gen.value -= 0.01
        def mod_001(gen):
            gen.value = gen.value - gen.value%0.01
        def mod_01(gen):
            gen.value = gen.value - gen.value%0.1
        def mod_1(gen):
            gen.value = gen.value - gen.value%1
        def mod_10(gen):
            gen.value = gen.value - gen.value%10
        def mod_100(gen):
            gen.value = gen.value - gen.value%100

        int_list = [Mutation(mutate = add_1),
            Mutation(mutate = sub_1),
            Mutation(mutate = mul_1),
            Mutation(mutate = add_10),
            Mutation(mutate = sub_10),
            Mutation(mutate = mul_10),
            Mutation(mutate = add_100),
            Mutation(mutate = sub_100),
            Mutation(mutate = mul_100),
            Mutation(mutate = mod_10),
            Mutation(mutate = mod_100)]

        float_list =[*int_list,
            Mutation(mutate = div_1),
            Mutation(mutate = div_10),
            Mutation(mutate = div_100),
            Mutation(mutate = add_05),
            Mutation(mutate = add_01),
            Mutation(mutate = add_001),
            Mutation(mutate = sub_05),
            Mutation(mutate = sub_01),
            Mutation(mutate = sub_001),
            Mutation(mutate = mod_1)]

    class Val():
        """Private Class"""
        def not_null(gen):
            if not gen.value:
                gen.value = 1 

        def simplify_frac(gen):
            d1 = gen.individual.gens[gen.names[0]]
            d2 = gen.individual.gens[gen.names[1]]

            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 
                53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

            for p in primes:
                while True:
                    if not (d1.value%p) and not (d2.value%p):
                        d1.value /= p
                        d2.value /= p
                        continue
                    break

            if d2.value < 0:
                d2.value *= -1
                d1.value *= -1

            d1.value = int(d1.value)
            d2.value = int(d2.value)

        not_null_list = [Validation(validate = not_null)]
        simplify_frac_list = [Validation(validate = simplify_frac)]

    int_mut_list = Mut().int_list
    float_mut_list = Mut().float_list

    class IntGen(ValuableGen):
        """Public Class
        IntGen represents an integer value."""
        def __init__(self, mutation_list = None, value = 0, validation_list = []):
            if not mutation_list: mutation_list = Default.int_mut_list
            ValuableGen.__init__(self, mutation_list = mutation_list, value = value, validation_list = validation_list) 

    class FltGen(ValuableGen):
        """Public Class
        FltGen represents an float value."""
        def __init__(self, mutation_list = None, value = 0, validation_list = []):
            if not mutation_list: mutation_list = Default.float_list
            ValuableGen.__init__(self, mutation_list = mutation_list, value = value, validation_list = validation_list) 
            
    class FracGen(RunnableGen):
        """Public Class
        FracGen represents an float value get by the division of two integers."""
        def __init__(self, names = [], individual = None, req_gens = {},mutation_list = [], validation_list = []):
            if names or len(names) != 2: 
                names = [str(random.randint(0,99)) + 'd' + str(x+1) for x in range(2)]

            r1 = GenBuffer(gen_class = Default.IntGen,
                new_instace = self.get_gen(validation_list = Default.Val.not_null_list, value = 1))
            r2 = GenBuffer(gen_class = Default.IntGen, 
                new_instace = self.get_gen(value = 1))

            RunnableGen.__init__(self, 
                req_gens = {names[0]:r2, names[1]:r1},
                    validation_list = Default.Val.simplify_frac_list,
                    names = names, individual = individual, mutation_list = mutation_list)

        def run(self, param):
            up = self.individual.gens[self.names[0]].value
            down = self.individual.gens[self.names[1]].value
            return up/down

        def get_gen(self, **param):
            def get():
                return Default.IntGen(**param)
            return get

        def __str__(self):
            self.validade()
            up = self.individual.gens[self.names[0]].value
            down = self.individual.gens[self.names[1]].value            
            return (str(up) + ('/' + str(down) if (down - 1) else ''))