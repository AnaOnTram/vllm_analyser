from matplotlib import pyplot as plt
import csv, statistics

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
                model_name = model_name.replace('/', '_')
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
        plt.plot(range(len(drafts)), drafts, color='blue', label='draft_speed', linestyle='-.')
        plt.plot(range(len(acceptance)), acceptance, color='orange', label='acceptance_rate', linestyle=':')
        plt.ylabel('decode speed')
        plt.legend()
        plt.title(f'{model_name} Speculative Performance')
        plt.savefig(f'{model_name}_perf.png', dpi=300)
        plt.show()

    if len(acceptance) > 2:
        new_file = open(f'{model_name}_performance.csv', 'w', newline='')
        new_writer = csv.DictWriter(new_file, ['Prefill', 'Decode', 'Average Acceptance Rate'])
        new_writer.writeheader()
        number = min(len(prefill), len(decode), len(acceptance))
        for i in range(number):
            new_writer.writerow({'Prefill': prefill[i], 'Decode': decode[i], 'Average Acceptance Rate': acceptance[i]})
    else: 
        new_file = open(f'{model_name}_performance.csv', 'w', newline='')
        new_writer = csv.DictWriter(new_file, ['Prefill', 'Decode'])
        new_writer.writeheader()
        number = min(len(prefill), len(decode))
        for i in range(number):
            new_writer.writerow({'Prefill': prefill[i], 'Decode': decode[i]})
    
    new_file.close()
    print(f'Average Decode Speed: {statistics.mean(decode)}')
    print(f'Decode Speed Standard Deviation: {statistics.stdev(decode)}')
    if len(acceptance) > 2:
        print(f'MTP Avarage Acceptance Rate: {statistics.mean(acceptance)}%')
        print(f'MTP Acceptance Rate Standard Deviation: {statistics.stdev(acceptance)}%')
        if statistics.mean(acceptance) <= 50:
            print('You may consider decrease "num_speculative_tokens" value to increase decode performance.')

except:
    print('Input Error! Cannot Find the file. Please check your input and re-run the programme.')