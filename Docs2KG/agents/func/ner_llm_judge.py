from loguru import logger

from Docs2KG.agents.manager import AgentManager


class NERLLMJudge:
    def __init__(self, agent_name="phi3.5", agent_type="ollama", **kwargs):
        self.llm = AgentManager(agent_name, agent_type, **kwargs)

    def judge(self, ner, ner_type, text):
        prompt = f"""You are a expert judge to evaluate whether within the following text: '{text}'
                    the named entity '{ner}' is of type '{ner_type}'.
                    Whether it is properly identified or not, please provide your judgement.

                    Return in JSON format with key result, and value either 'correct' or 'incorrect'.

                    """

        response = self.llm.process_input(prompt)
        logger.debug(f"LLM response: {response}")

        if "incorrect" in response["response"]:
            logger.warning("LLM judgement: incorrect")
            logger.warning(
                f"Entity {ner}/ type {ner_type} is incorrect for text: {text}"
            )
            return False
        else:
            logger.critical("LLM judgement: correct")
            return True
