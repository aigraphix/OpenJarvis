import asyncio
from openjarvis.tools.parallel_delegate import ParallelDelegateTasksTool
from dotenv import load_dotenv

def test_parallel_tool():
    load_dotenv()
    
    tool = ParallelDelegateTasksTool()
    
    tasks = [
        {
            "agent_name": "architect",
            "task": "Test #1 (Architect): Pitch an idea for a smart watch OS. 1 sentence max."
        },
        {
            "agent_name": "critic",
            "task": "Test #2 (Critic): Criticize smart watch OS idea. 1 sentence max."
        },
        {
            "agent_name": "coder",
            "task": "Test #3 (Coder): Write 1 line of python for a smart watch."
        }
    ]
    
    print("Executing parallel delegation tool, starting tests...")
    result = tool.execute(tasks=tasks)
    
    print("\\nTOOL SUCCESS:", result.success)
    print("TOOL CONTENT:\\n")
    print(result.content)

if __name__ == "__main__":
    test_parallel_tool()
