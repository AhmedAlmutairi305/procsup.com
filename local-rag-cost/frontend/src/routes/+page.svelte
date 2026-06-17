<script lang="ts">
  import { chat } from '$lib/api';

  let workspace = 'demo';
  let query = '';
  let answer = '';
  let cost: any = null;

  async function send() {
    const data = await chat(workspace, query);
    answer = data.answer;
    cost = data.cost_breakdown;
  }
</script>

<h1>Local RAG Chat</h1>
<input bind:value={workspace} placeholder="workspace" />
<textarea bind:value={query} placeholder="Ask a question"></textarea>
<button on:click={send}>Send</button>

{#if answer}
  <h2>Answer</h2>
  <p>{answer}</p>
{/if}

{#if cost}
  <div>
    <h3>Cost Summary</h3>
    <p>Input tokens: {cost.input_tokens}</p>
    <p>Output tokens: {cost.output_tokens}</p>
    <p>USD: {cost.cost_usd}</p>
  </div>
{/if}
