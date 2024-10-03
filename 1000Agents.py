import random
import tabulate
from colorama import init, Fore
import ollama

init()  # Initialize colorama

def generate_biography(agent_name, max_retries=3):
    prompt = f"""
    System: You as a experienced random-biography-inventor. Generate one short, random and unique biography for {agent_name} with an interesting career in any professional enterprise field like engineering, science, marketing, administration, finance, etc. Use exactly the following items: 
    Human Name, Age, Sex, Education, Profession, Profession, Special skills, Hobbies, etc.
    """

    prompt = prompt.replace("\n", "").replace("\t", "").strip()
    messages = [{'role': 'system', 'content': prompt}]
    retries = 0
    while retries < max_retries:
        try:
            response = ollama.chat(model='zephyr:latest', messages=messages)
            biography = response['message']['content']
            if biography.strip():  # Check if the biography is not empty
                return biography
            else:
                retries += 1
                print(f"Empty response received. Retrying ({retries}/{max_retries})")
        except Exception as e:
            print(f"Error generating biography: {e}")
            retries += 1
            print(f"Error occurred. Retrying ({retries}/{max_retries})")
    return "Biography generation failed. Please try again."

class Agent:
    def __init__(self, name, model_name):
        self.name = name
        self.model_name = model_name
        self.biography = generate_biography(name)

    def print_biography(self):
        return [self.name, self.biography]

    def respond(self, prompt, system_prompt, context):
        if context is None:
            context = f"Agent: {self.name}\nBiography: {self.biography}\nSystem Prompt: {system_prompt}\n"
        context = f"Agent: {self.name}\nBiography: {self.biography}\nSystem Prompt: {system_prompt}\nConversation: {context}\n"
        messages = [{'role': 'system', 'content': context}, {'role': 'user', 'content': prompt}]
        response = ollama.chat(model=self.model_name, messages=messages)
        return response['message']['content']

def start_conversation(agents, prompt, system_prompt, conversation, max_responses=3, verbose=True):
    participants = random.sample(agents, random.randint(3, 5))

    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
    for _ in range(max_responses):
        for agent in participants:
            response = agent.respond(prompt, system_prompt, conversation)
            conversation.append(f"{agent.name}: {response}")
            prompt = response  # Update the prompt for the next agent
            if verbose:
                print(f"{random.choice(colors)}{agent.name} responded: {response}{Fore.RESET}")
                print("\n")
    return conversation

def interact_agents(agents, user_prompt, system_prompt):
    conversation_count = 0
    conversation = []
    while True:
        conversation = start_conversation(agents, user_prompt, system_prompt, conversation, verbose=True)
        conversation_count += 1
        print(f"Conversation {conversation_count} completed.")

       # Generate a summary of the conversation using the zephyr:latest model
        summary_prompt = "Summarize the following conversation:\n\n" + "\n".join(conversation)+ "\n\n Do not add anything, use only the conversation to create the summary!"
        messages = [{'role': 'system', 'content': summary_prompt}]
        summary_response = ollama.chat(model='zephyr:latest', messages=messages)
        summary = summary_response['message']['content']

        summary_prompt = "Do a very critical, short evaluation if the summary supports the task in the user prompt: \n\nUser prompt: \n\n" + (user_prompt) + "\n\n Summary of the conversation:\n" + "\n" + (summary) + "\n\n Do not add anything, use only the summary and the user prompt to evaluate if the summary supports the user prompt"
        messages = [{'role': 'system', 'content': summary_prompt}]
        evaluation_response = ollama.chat(model='zephyr:latest', messages=messages)
        evaluation = evaluation_response['message']['content']
        summary = "Summary: " + summary + "\n\nUser prompt: " + user_prompt +"\n\nEvaluation: " + evaluation 
        
        print("\n" + "-" * 80 + "\n")
        print(f"\nSummary of the conversation:\n" + "-" * 80 + f"\n{summary}")
        print("\n" + "-" * 80 + "\n")
        
        # Replace the conversation with the summary
        conversation = [f"Background from previous conversation: {summary}"]
        
        if conversation_count % 10 == 0:
            participate = input("Do you want to participate in the next conversation? (yes/no): ")
            if participate.lower() != "yes":
                break

def print_biographies(agents):
    biographies_table = [agent.print_biography() for agent in agents]
    biographies_table.insert(0, ["Agent", "Biography"])
    print(tabulate.tabulate(biographies_table, headers="firstrow", tablefmt="simple"))
#    print(tabulate.tabulate(biographies_table, headers="firstrow", tablefmt="grid"))
    print("-" * 80)
    print(agent.print_biography() for agent in agents)
    print("-" * 80)

# first ask about the theam 
agents = [Agent(f"Agent_{i}", 'llama3.2:3b-instruct-fp16') for i in range(10)]

print_biographies(agents)

system_prompt = """
    Let's have a lively, controversy but prductive conversation about the USER PROMPT. 
    Use your unique expertise and your individual background. 
    If you don't have anything interesting to say, just say so. Don't try to force it. 
    If you can contribute new insights, GIVE SHORT ANSWERS of up to ONLY 5 sentences! 
    Only if you have a realy good and unique idea, you can give a answer of up to 10 sentences. 
    If this idee isn't that good, you will be penalized in the evaluation! 
    Watch the conversation history, especially your own previous statements and restrict your responses only to new aspects. 
    Analyze the previous statements critically and try to do better! 
    Because your previous answer was to long and unproductive, you will be penalized in the evaluation by -2! 
    *** DO NOT REPEAT any previous answer! 
    *** DO NOT introduce yourself! If you are referring to another agent's speech, mention his name. 
    *** Give productive answers to force a solution to the problem and be focused on the users problem! 
    If discussion stucks, take a step back and try another approach. 
    If disscussion is not anymore supporting user prompt, take two steps back and try to get back to the user prompt. 
    *** ALLWAYS take into account the user prompt! 
"""

user_prompt = input("Enter a prompt to start the conversation: ")
interact_agents(agents, user_prompt, system_prompt)