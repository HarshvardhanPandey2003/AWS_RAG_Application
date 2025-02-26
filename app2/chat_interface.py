# chat_interface.py
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from typing import List, Tuple
import numpy as np
from llm import get_llm

class ChatInterface:
    def __init__(self, embeddings_data: dict):
        self.chunks = embeddings_data['chunks']
        self.faiss_index = embeddings_data['faiss_index']
        self.embeddings = embeddings_data['embeddings']
        self.embeddings_model = embeddings_data.get('embeddings_model')
        self.memory = ConversationBufferMemory()
        self.llm = get_llm()
        
    def _get_relevant_context(self, query: str, k: int = 3) -> str:
        """Retrieve relevant context using FAISS similarity search"""
        try:
            # If we have the embeddings model in the data
            if self.embeddings_model:
                query_embedding = np.array(
                    self.embeddings_model.embed_query(query)
                ).reshape(1, -1)
            else:
                # Fall back to using the first embedding's dimension
                dimension = len(self.embeddings[0])
                query_embedding = np.zeros((1, dimension))
            
            D, I = self.faiss_index.search(query_embedding.astype('float32'), k)
            relevant_chunks = [self.chunks[i] for i in I[0]]
            return "\n".join(relevant_chunks)
        except Exception as e:
            print(f"Error in _get_relevant_context: {str(e)}")
            return ""

    def generate_response(self, user_input: str) -> str:
        try:
            # Get relevant context
            context = self._get_relevant_context(user_input)
            
            # Create a prompt template for this specific interaction
            prompt_template = PromptTemplate(
                input_variables=["history", "input", "context"],
                template=(
                    "You are an AI assistant helping with PDF document questions.\n"
                    "Previous conversation:\n{history}\n\n"
                    "Relevant PDF content:\n{context}\n\n"
                    "Human: {input}\n"
                    "Assistant: "
                )
            )
            
            # Get conversation history
            history = self.memory.load_memory_variables({})
            history_str = history.get("history", "")
            
            # Format the prompt
            prompt = prompt_template.format(
                history=history_str,
                input=user_input,
                context=context
            )
            
            # Generate response
            response = self.llm.predict(prompt)
            
            # Update memory
            if history_str:
                self.memory.save_context(
                    {"input": user_input},
                    {"output": response}
                )
            else:
                # First interaction
                self.memory = ConversationBufferMemory(memory_key="history")
                self.memory.save_context(
                    {"input": user_input},
                    {"output": response}
                )
            
            return response
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error processing your question. Please try again."

#