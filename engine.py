from matplotlib import pyplot as plt
import argparse, csv, statistics, numpy as np

parser = argparse.ArgumentParser(prog='engine.py')
parser.add_argument('-f', '--file', type=str, help="Path to the log file",)
parser.add_argument('-e', '--engine', type=int, choices=[0,1,2], help="0 for vllm, 1 for sglang, 2 for llama.cpp",)
args = parser.parse_args()

prefill = list()
decode = list()
drafts = list()
acceptance = list()
engine = ['vllm', 'sglang', 'llama.cpp']
    
target = args.file
inference_select = args.engine

if inference_select in range(len(engine)):
    print(f'Inference Engine Selected: {engine[inference_select]}')
else:
    print('Input range should be within: 0-2')

file = open(target, 'r')
if engine[inference_select] == 'sglang':
    for line in file:
        line_components = line.strip().split()
        if 'Found local HF snapshot for' in line:
            sg1 = line_components.index('snapshot')
            model_name = line_components[sg1+2]
            model_name = model_name.replace('/', '_')
            print(f'Served Model: {model_name}')
        if 'Prefill batch' in line:
            sg2 = line_components.index('(token/s):')
            prefill_speed = float(line_components[sg2+1])
            if prefill_speed > 0:
                prefill.append(prefill_speed)
        if 'Decode batch' in line:
            sg3 = line_components.index('(token/s):')
            decode_speed = float(line_components[sg3+1][:-1])
            if decode_speed > 0:
                decode.append(decode_speed)
        if 'accept rate' in line:
            sg4 = line_components.index('accept')
            accept_rate = float(line_components[sg4+5][:-1])*100
            acceptance.append(accept_rate)

if engine[inference_select] == 'vllm':
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
                if prefill_speed != 0:
                    prefill.append(prefill_speed)
                if decode_speed != 0:
                    decode.append(decode_speed)
            if '[metrics.py:101]' in components:
                #print(components)
                sp3 = components.index('Drafted')
                sp4 = components.index('Avg')
                draft_throughput = float(''.join(components[sp3+2:sp3+3]))
                avg_accept = float(''.join(components[sp4+4:sp4+5])[:4])
                if draft_throughput != 0:
                    drafts.append(draft_throughput)
                if avg_accept != 0:
                    acceptance.append(avg_accept)

if engine[inference_select] =='llama.cpp':
    print('llama.cpp not supported yet! Please stay tune for update.')

plt.plot(range(len(prefill)), prefill, color='green')
plt.ylabel('Prefill Speed')
plt.title(f'{model_name} Prefill Performance')
plt.show()
    
    
plt.plot(range(len(decode)), decode, color='red')
plt.ylabel('decode speed')
plt.title(f'{model_name} Decode Performance')
plt.show()

plt.plot(range(len(prefill)), prefill, color='green', label='Prefill')
plt.plot(range(len(decode)), decode, color='red', label='Decode')
plt.title(f'{model_name} Inference Performance')
plt.legend()
plt.savefig(f'{model_name}_perf.png', dpi=300)
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

peak_prefill_speed = max(prefill)
min_prefill_speed = min(prefill)
peak_decode_speed = max(decode)
min_decode_speed = min(decode)
avg_prefill_speed = statistics.mean(prefill)
avg_decode_speed = statistics.mean(decode)
per_95_prefill = np.percentile(prefill, 95)
per_95_decode = np.percentile(decode, 95)

print('-'*25+'Basic'+'-'*25)
print(f'Peak Prefill Speed is: {peak_prefill_speed} tokens/second')
print(f'Minimum Prefill Speed is: {min_prefill_speed} tokens/second')
print(f'Average Prefill Speed is: {avg_prefill_speed:.2f} tokens/second')
print(f'95th percentile of Prefill Speed is: {per_95_prefill:.2f} tokens/second')
print(f'Peak Decode Speed is: {peak_decode_speed} tokens/second')
print(f'Minimum Deocde Speed is: {min_decode_speed} tokens/second')
print(f'Average Decode Speed is: {avg_decode_speed:.2f} tokens/second')
print(f'95th percentile of Docode Speed is: {per_95_decode:.2f} tokens/second')
print('-'*25+'MTP'+'-'*25)
if len(acceptance) > 2:
    max_acceptance = max(acceptance)
    min_acceptance = min(acceptance)
    avg_acceptance = statistics.mean(acceptance)
    per_95_acceptance = np.percentile(acceptance, 95)
    print(f'Peak accept rate is: {max_acceptance:.2f}%')
    print(f'Minimum accept rate is: {min_acceptance:.2f}%')
    print(f'Average accept rate is: {avg_acceptance:.2f} %')
    print(f'95th percentile of accept rates is: {per_95_acceptance:.2f}%')
    if per_95_acceptance <= 50:
        print('Try reduce your number of draft tokens to avoid overhead!')