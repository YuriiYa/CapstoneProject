# filepath: c:\projects\AI Academy\CapstoneProject\src\agent\rag_agent_base.py
class RAGAgentBase:
    """Shared RAG pipeline logic for CLI and API."""

    def _process_query_common(
        self,
        question: str,
        include_reasoning: bool,
        verbose: bool,
        generate_linkedin_post: bool,
        post_tone: str,
        post_length: str,
        return_post_as_answer: bool,
    ):
        if verbose:
            print(f"Question: {question}")

        # 1. Analyze query
        if verbose:
            print("🔍 1. Analyze query...")
        analysis = self.reasoning_engine.analyze_query(question)
        if verbose:
            print(f"   Intent: {analysis.get('intent', 'unknown')}")
            print(f"   Complexity: {analysis.get('complexity', 'unknown')}")
            print("")

        # 2. Retrieve context
        if verbose:
            print("📚 2. Retrieving context...")
        context = self.retriever.retrieve(question, top_k=self.TOP_K)
        if context and verbose:
            print(f" Retrieved {len(context)} relevant chunks")
            print(f"\n📖 Sources:")
            for i, ctx in enumerate(context, 1):
                metadata = ctx.get('metadata', {})
                source = metadata.get('source', 'Unknown')
                similarity = ctx.get('similarity', 0.0)
                document = ctx.get('document', '')
                print(f"   {i}. {source} (similarity: {similarity:.2%}):{document}")

        # 3. Determine if tools needed
        tool_results = []
        if verbose:
            print(" # 3. Determine if tools needed")
        if analysis.get('requires_tools', False):
            tools = analysis.get('suggested_tools', [])
            for tool_name in tools:
                result = self.tool_manager.execute_tool(tool_name, query=question)
                if result.get('success'):
                    tool_results.append(result)
                    if verbose:
                        print(f"Needed tool: {tool_name}, Result: {result}")

        # 4. Generate answer
        context_text = self.PromptTemplates.format_context(context)
        prompt = self.PromptTemplates.rag_query_template(context_text, question)
        answer = self.llm_client.generate(
            prompt,
            max_tokens=self.MAX_TOKENS,
            temperature=self.TEMPERATURE
        )

        print(f"Answer before reflection: {answer}\n") if verbose else None

        # 5. Reflect on answer
        reflection = self.reflection_module.reflect(question, context, answer)
        if reflection.get('issues') and verbose:
            print(f"⚠ Issues identified: {', '.join(reflection['issues'])}")

        # 6. Self-correct if needed
        if reflection.get('needs_correction', False):
            answer = self.self_correct(question, context, answer, reflection)
            reflection = self.reflection_module.reflect(question, context, answer)

        # 7. Generate LinkedIn post
        post = None
        if generate_linkedin_post:
            if verbose:
                print("📱 Generating LinkedIn post...")
            try:
                linkedin_prompt = (
                    "Create a LinkedIn post based on the following content.\n"
                    f"Tone: {post_tone}\n"
                    f"Length: {post_length}\n"
                    "Keep it professional, clear, and engaging.\n\n"
                    f"Content:\n{answer}"
                )
                post = self.post_generator.generate_custom_post(
                    custom_prompt=linkedin_prompt
                )
                if verbose:
                    print("\n" + "━" * 60)
                    print("📱 LinkedIn Post:")
                    print("━" * 60 + "\n")

                    if post:
                        print(post + "\n")
                        print("━" * 60)
                        print(f"Characters: {len(post)}/{self.LINKEDIN_POST_MAX_CHARS}")
                    else:
                        print("Generation failed.\n")
                    print()
            except Exception as e:
                if verbose:
                    print(f"LinkedIn post generation error: {e}\n")

        if return_post_as_answer and post:
            answer = post

        result = {
            "answer": answer,
            "confidence": reflection.get('confidence', self.CONFIDENCE),
            "sources": [
                {
                    "source": c.get('metadata', {}).get('source', 'Unknown'),
                    "similarity": c.get('similarity', 0.0)
                }
                for c in context
            ]
        }

        if include_reasoning:
            result.update({
                "reasoning": {
                    "intent": analysis.get('intent'),
                    "complexity": analysis.get('complexity'),
                    "key_concepts": analysis.get('key_concepts', [])
                },
                "reflection": {
                    "scores": reflection.get('scores', {}),
                    "issues": reflection.get('issues', [])
                },
                "context_count": len(context),
                "tools_used": [t.get('tool') for t in tool_results]
            })

        return result
