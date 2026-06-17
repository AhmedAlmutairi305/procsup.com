<script lang="ts">
  import { providers } from '$lib/api';
  let items: string[] = [];
  providers().then((d) => (items = d.providers));
</script>

<h1>Providers (read-only)</h1>
<ul>
  {#each items as p}
    <li>{p}</li>
  {/each}
</ul>
