from matplotlib import pyplot as plt

file = open('log.txt', 'r')
prefill = list()
decode = list()
drafts = list()
acceptance = list()

target = input('Please input your log file name (e.g. log.txt): ')

try:
    file = open(target, 'r')
    for line in file:
        if line.startswith('(APIServer pid=28) INFO'):
            components = line.strip().split(' ')
            if '[utils.py:233]' in components:
                sp0 = components.index("{'model_tag':")
                model_name = ''.join(components[sp0 + 1: sp0 + 2])[1:-2]
            if '[loggers.py:271]' in components:
                sp1 = components.index('throughput:')
                sp2 = components[sp1+1:].index('throughput:')
                prefill_speed = float(''.join(components[sp1 + 1:sp1 + 2]))
                decode_speed = float(''.join(components[sp1+sp2+2:sp1+sp2+3]))
                prefill.append(prefill_speed)
                decode.append(decode_speed)
            if '[metrics.py:101]' in components:
                #print(components)
                sp3 = components.index('Drafted')
                sp4 = components.index('Avg')
                draft_throughput = float(''.join(components[sp3+2:sp3+3]))
                avg_accept = float(''.join(components[sp4+4:sp4+5])[:4])
                drafts.append(draft_throughput)
                acceptance.append(avg_accept)
                
    plt.plot(range(len(prefill)), prefill, color='green')
    plt.ylabel('Prefill Speed')
    plt.title(f'{model_name} Prefill Performance')
    plt.show()
    
    
    plt.plot(range(len(decode)), decode, color='red')
    plt.ylabel('decode speed')
    plt.title(f'{model_name} Decode Performance')
    plt.show()
    
    
    if len(acceptance) > 2:
        plt.plot(range(len(acceptance)), acceptance, color='blue')
        plt.ylabel('Acceptance Rate')
        plt.title(f'{model_name} MTP Performance')
        plt.show()
    
        plt.plot(range(len(decode)), decode, color='red', label='decode')
        plt.plot(range(len(drafts)), drafts, color='blue', label='draft', linestyle='-.')
        plt.plot(range(len(acceptance)), acceptance, color='orange', label='draft', linestyle=':')
        plt.ylabel('decode speed')
        plt.legend()
        plt.title(f'{model_name} Speculative Performance')
        plt.savefig('{model_name}_perf.png', dpi=300)
        plt.show()
except:
    print('Input Error! Cannot Find the file. Please check your input and re-run the programme.')
