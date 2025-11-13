<script>
  import { useSvelteFlow } from '@xyflow/svelte';
  import { onMount } from 'svelte';

  export let commandQueue = [];

  const { fitView, setCenter } = useSvelteFlow();

  // Process commands from parent
  $: if (commandQueue.length > 0) {
    const command = commandQueue[commandQueue.length - 1];
    executeCommand(command);
  }

  async function executeCommand(command) {
    if (!command) return;

    switch (command.type) {
      case 'fitToNode':
        await fitView({
          nodes: [{ id: command.nodeId }],
          maxZoom: 1,
          duration: 300,
          padding: 0.2
        });
        break;

      case 'centerOnNode':
        if (command.position) {
          await setCenter(command.position.x, command.position.y, {
            zoom: command.zoom || 1,
            duration: 300
          });
        }
        break;

      case 'goToTop':
        if (command.nodeId) {
          await fitView({
            nodes: [{ id: command.nodeId }],
            maxZoom: 1,
            duration: 300,
            padding: 0.2
          });
        }
        break;
    }
  }
</script>

<!-- This component has no UI, it just provides flow control -->
