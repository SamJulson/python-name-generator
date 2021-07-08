import random
import sys
import os

from dataclasses import dataclass, field

@dataclass
class Command_Type:
    name: str
    num_args: int
    arg_types: list

@dataclass
class COMMAND_TYPES:
    NULL = Command_Type("none", 0, [])
    EXIT = Command_Type("exit", 0, [])
    CLEAR = Command_Type("clear", 0, [])
    NEW_GEN = Command_Type("newgen", 0, [])
    SELECT = Command_Type("select", 1, [str])
    NEXT_GEN = Command_Type("nextgen", 0, [])
    PRINT_GEN = Command_Type("printgen", 0, [])
    SET = Command_Type("set", 2, [str, object])
    PRINT = Command_Type("print", 1, [str])
    REDO = Command_Type("redo", 0, [])

@dataclass
class Command:
    type: Command_Type
    args: list = field(default_factory=lambda: [])

@dataclass
class GeneratorState:
    population: list = field(default_factory=lambda: [])
    survived: list = field(default_factory=lambda: [])

    min_length: int = 3
    max_length: int = 10
    mutation_rate: float = 0.2
    population_size: int = 20
    random_selection: int = 2

    def populationList(self) -> str:
        output = ''
        for i, v in enumerate(self.population):
            output += f'{i}. {v}\n'
        return output


def randomCharacter() -> str:
    return chr(random.randint(97, 122))

def containsVowels(s: str) -> bool:
    vowels = {'a', 'e', 'i', 'o', 'u'}
    return len(vowels.intersection(set(s))) != 0

def randomWordString(min_length: int, max_length: int, max_consonant_count: int = 3) -> str:
    consonants = {'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z'}
    vowels = {'a', 'e', 'i', 'o', 'u'}

    def generateWordString():
        s = ''
        consonant_count = 0
        for _ in range(random.randint(min_length, max_length)):
            if consonant_count > max_consonant_count:
                s += random.choice(list(vowels))
                consonant_count = 0
            else:
                newLetter = random.choice(list(consonants.union(vowels)))
                s += newLetter
                if newLetter in vowels:
                    consonant_count = 0
                else:
                    consonant_count += 1
        return s
    
    w = generateWordString()
    while not containsVowels(w):
        w = generateWordString()
    return w

def crossoverStrings(a: str, b: str, min_length: int, max_length: int) -> str:

    vowels = {'a', 'e', 'i', 'o', 'u'}

    def crossStrings():
        new_length = random.randint(min_length, min(max_length, len(a)+len(b)))
        firstHalf = bool(random.randint(0,1))

        if firstHalf:
            splice = random.randint(1, len(a)-1)
            newname = a[:splice] + b[splice:new_length-splice+1]
        else:
            splice = random.randint(1, len(b)-1)
            newname = b[:splice] + a[splice:new_length-splice+1]


        if (len(newname) > new_length):
            start = random.randint(0, len(newname) - new_length)
            end = start + new_length - 1
            newname = newname[start:end]
        return newname
    
    w = crossStrings()
    while not containsVowels(w):
        w = crossStrings()
    return w
    

def mutateString(s : str, mutation_rate : float = 0.2, min_length : int = 3, max_length : int = 7) -> str:

    def mutateWord():
        newString = ''
        for _, v in enumerate(s):
            if random.random() < mutation_rate:
                if len(s) <= max_length and (len(s) <= min_length or bool(random.randint(0,1))):
                    newString += randomCharacter()
                else:
                    continue
            else:
                newString += v
        while len(newString) < max_length and random.random() < mutation_rate:
            newString += randomCharacter()
        return newString
    
    w = mutateWord()
    while not containsVowels(w):
        w = mutateWord()
    return w
    
def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def evaluate(c : Command, s: GeneratorState) -> str:

    def exit(args):
        sys.exit()
    
    def clear(args: list):
        clearScreen()

    def newgen(args: list) -> str:
        s.population = []
        s.survived = []
        for _ in range(s.population_size):
            s.population.append(randomWordString(s.min_length, s.max_length))
        return s.populationList()
    
    def select(args: list) -> str:
        if args[0] in s.population:
            s.survived.append(args[0])
            return f'Selected "{args[0]}"'
        else:
            try:
                if int(args[0]) < len(s.population):
                    s.survived.append(s.population[int(args[0])])
                    return f'Selected "{s.population[int(args[0])]}"'
            except ValueError:
                return 'Invalid selection.'
    
    def nextgen(args: list) -> str:
        if len(s.survived) < 2:
            while len(s.survived) < s.random_selection:
                choice = random.choice(s.population)
                s.population.remove(choice)
                s.survived.append(choice)
        s.population = []
        return populate()

    def populate() -> str:
        for _ in range(s.population_size):
            s1 = random.choice(s.survived)
            s.survived.remove(s1)
            s2 = random.choice(s.survived)
            s.population.append(mutateString(crossoverStrings(s1, s2, s.min_length, s.max_length), s.mutation_rate, s.min_length, s.max_length))
            s.survived.append(s1)
        return s.populationList()

    def redo(args: list) -> str:
        s.population = []
        return populate()
    
    def printgen(args: list) -> str:
        return s.populationList()
    
    def setVar(args: list) -> str:
        try:
            attrType = type(getattr(s, args[0]))
        except Exception:
            return 'Invalid variable name. For more information, try "help set".'
        finally:
            setattr(s, args[0], attrType(args[1]))
            return f'Set {args[0]} = {args[1]}'

    def printVar(args: list) -> str:
        try:
            getattr(s, args[0])
        except Exception:
            return 'Invalid variable name. For more information, try "help print".'
        finally:
            return f'{args[0]} = {getattr(s, args[0])}'
        
    options = {
        COMMAND_TYPES.NULL.name : lambda args: None,
        COMMAND_TYPES.EXIT.name : exit,
        COMMAND_TYPES.CLEAR.name : clear,
        COMMAND_TYPES.NEW_GEN.name : newgen,
        COMMAND_TYPES.SELECT.name : select,
        COMMAND_TYPES.NEXT_GEN.name : nextgen,
        COMMAND_TYPES.PRINT_GEN.name : printgen,
        COMMAND_TYPES.SET.name : setVar,
        COMMAND_TYPES.PRINT.name : printVar,
        COMMAND_TYPES.REDO.name : redo,
    }

    return options[c.type.name](c.args) or ''

def read() -> Command:
    inputList = input("> ").split()

    options = {
        "quit" : COMMAND_TYPES.EXIT,
        "exit" : COMMAND_TYPES.EXIT,
        "clear" : COMMAND_TYPES.CLEAR,
        "newgen" : COMMAND_TYPES.NEW_GEN,
        "select" : COMMAND_TYPES.SELECT,
        "nextgen" : COMMAND_TYPES.NEXT_GEN,
        "printgen" : COMMAND_TYPES.PRINT_GEN,
        "set" : COMMAND_TYPES.SET,
        "print" : COMMAND_TYPES.PRINT,
        "redo" : COMMAND_TYPES.REDO,
    }

    command_type = COMMAND_TYPES.NULL
    if len(inputList) > 0:
        if inputList[0] in options.keys():
            command_type = options[inputList[0]]

    command_args = []
    for i in range(command_type.num_args):
        arg = inputList[i+1]
        try:
            if command_type.arg_types[i] != object:
                arg = command_type.arg_types[i](arg)
        except ValueError:
            print("Invalid Arguments.")
            return Command(COMMAND_TYPES.NULL, [])
        finally:
            command_args.append(arg)

    return Command(command_type, command_args)
    
def init() -> GeneratorState:
    print("Welcome to the name generator. Type 'help' for commands and usage.")
    s = GeneratorState()
    for _ in range(s.population_size):
        s.population.append(randomWordString(s.min_length, s.max_length))
    for _ in range(s.random_selection):
        s.survived.append(random.choice(s.population))
    return s

if __name__ == '__main__':
    clearScreen()
    s = init()
    while True:
        print(evaluate(read(), s))
