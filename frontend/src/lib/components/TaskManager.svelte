<script>
  import { onMount, tick } from 'svelte';
  import { fetchTasks, createTask, updateTask, deleteTask, fetchVersions, createVersion, updateVersion, deleteVersion as deleteVersionApi, reorderVersions, reorderTasks } from '../services/api.js';
  import { showToast } from '../stores/store.js';
  import { ChevronDown, ChevronRight } from 'lucide-svelte';

  export let onClose = () => {};
  export let inline = false; // When true, renders as inline content without modal backdrop

  const STATUSES = ['todo', 'in_progress', 'done'];
  const STATUS_LABELS = {
    todo: 'To Do',
    in_progress: 'In Progress',
    done: 'Done'
  };

  const INITIAL_VERSIONS = ['backlog', 'v1', 'v2'];
  let hiddenDefaultVersions = []; // Default versions that have been "deleted" (hidden)
  let customVersions = []; // User-added versions
  let versionLabels = {
    backlog: 'Backlog',
    v1: 'Version 1',
    v2: 'Version 2'
  };

  let tasks = [];
  let loading = true;
  let viewMode = 'kanban'; // 'kanban' or 'list'
  let showAddModal = false;
  let editingTask = null;
  let newTaskTitle = '';
  let newTaskDescription = '';
  let newTaskVersion = 'backlog';
  let visibleVersions = new Set(); // Set of visible version keys (empty = all visible)
  let collapsedVersions = new Set(); // Set of collapsed version keys

  // Quick add state
  let quickAddVersion = null;
  let quickAddStatus = null;
  let quickAddTitle = '';
  let quickAddInput = null;
  let isQuickAdding = false; // Prevent double submission

  // Task detail view state
  let viewingTask = null;
  let copiedTaskId = null;
  let copiedWithPlan = false;
  let deletingTask = null;

  // Versions menu state
  let showVersionsMenu = false;
  let showNewVersionInput = false;
  let newVersionName = '';
  let editingVersion = null;
  let editingVersionName = '';
  let deletingVersion = null;
  let deleteTargetVersion = 'backlog';
  let isDeleting = false;
  let draggedVersionItem = null;
  let dragOverVersionItem = null;

  // Ordered versions (for custom ordering) - backlog always last
  let versionOrder = ['v1', 'v2', 'backlog'];

  // Drag state
  let draggedTask = null;
  let dragOverColumn = null;
  let dragOverVersion = null;
  let dragOverTaskId = null; // For reordering within column

  // Reactive: filter tasks by status
  $: todoTasks = tasks.filter(t => t.status === 'todo');
  $: inProgressTasks = tasks.filter(t => t.status === 'in_progress');
  $: doneTasks = tasks.filter(t => t.status === 'done');

  // Reactive: get tasks by status
  $: tasksByStatus = {
    todo: todoTasks,
    in_progress: inProgressTasks,
    done: doneTasks
  };

  // Get visible default versions (initial minus hidden)
  $: visibleDefaultVersions = INITIAL_VERSIONS.filter(v => !hiddenDefaultVersions.includes(v));

  // Get unique versions from tasks and custom versions, respecting order
  $: allVersions = [...new Set([...versionOrder, ...customVersions, ...tasks.map(t => t.sprint || 'backlog')])].filter(v => !hiddenDefaultVersions.includes(v));
  // Sort versions with backlog always at the end
  $: versions = allVersions.sort((a, b) => {
    // Backlog always last
    if (a === 'backlog') return 1;
    if (b === 'backlog') return -1;

    const aIdx = versionOrder.indexOf(a);
    const bIdx = versionOrder.indexOf(b);
    if (aIdx === -1 && bIdx === -1) return 0;
    if (aIdx === -1) return 1;
    if (bIdx === -1) return -1;
    return aIdx - bIdx;
  });

  // Helper to sort tasks by sort_order
  function sortBySortOrder(taskList) {
    return [...taskList].sort((a, b) => (a.sort_order ?? 999999) - (b.sort_order ?? 999999));
  }

  // Reactive: swim lane data - combines versions with their tasks to ensure reactivity
  // Explicitly reference tasks.length to ensure Svelte tracks it as a dependency
  $: swimLaneData = (tasks.length, versions.map(version => ({
    version,
    label: versionLabels[version] || version,
    tasks: sortBySortOrder(tasks.filter(t => (t.sprint || 'backlog') === version)),
    isDefault: visibleDefaultVersions.includes(version),
    isCustom: !INITIAL_VERSIONS.includes(version) && customVersions.includes(version),
    byStatus: {
      todo: sortBySortOrder(tasks.filter(t => (t.sprint || 'backlog') === version && t.status === 'todo')),
      in_progress: sortBySortOrder(tasks.filter(t => (t.sprint || 'backlog') === version && t.status === 'in_progress')),
      done: sortBySortOrder(tasks.filter(t => (t.sprint || 'backlog') === version && t.status === 'done'))
    }
  })));

  // Filtered swim lane data based on visible versions
  $: filteredSwimLaneData = visibleVersions.size === 0
    ? swimLaneData
    : swimLaneData.filter(lane => visibleVersions.has(lane.version));

  // Check if all versions are visible
  $: allVersionsVisible = visibleVersions.size === 0;

  // Toggle version visibility
  function toggleVersionVisibility(version) {
    if (visibleVersions.size === 0) {
      // Currently showing all - switch to showing only this version
      visibleVersions = new Set([version]);
    } else if (visibleVersions.has(version)) {
      // Version is visible - hide it
      visibleVersions.delete(version);
      if (visibleVersions.size === 0) {
        // If none left, show all
        visibleVersions = new Set();
      } else {
        visibleVersions = new Set(visibleVersions);
      }
    } else {
      // Version is hidden - show it
      visibleVersions = new Set([...visibleVersions, version]);
    }
  }

  // Toggle all versions visibility
  function toggleAllVersions() {
    if (visibleVersions.size === 0) {
      // All visible - hide all (show none... actually keep at least one)
      visibleVersions = new Set();
    } else {
      // Some hidden - show all
      visibleVersions = new Set();
    }
  }

  // Check if a version is visible
  function isVersionVisible(version) {
    return visibleVersions.size === 0 || visibleVersions.has(version);
  }

  // Toggle version collapse state
  function toggleCollapse(version) {
    if (collapsedVersions.has(version)) {
      collapsedVersions.delete(version);
    } else {
      collapsedVersions.add(version);
    }
    collapsedVersions = new Set(collapsedVersions); // Trigger reactivity
  }

  // Check if a version is collapsed
  function isCollapsed(version) {
    return collapsedVersions.has(version);
  }

  // Get version label (supports custom versions)
  function getVersionLabel(version) {
    return versionLabels[version] || version;
  }

  // Get tasks by version and status
  function getTasksByVersionAndStatus(version, status) {
    return tasks.filter(t => (t.sprint || 'backlog') === version && t.status === status);
  }

  onMount(async () => {
    await Promise.all([loadTasks(), loadVersions()]);
    loading = false;
  });

  async function loadTasks() {
    try {
      const data = await fetchTasks();
      // Force reactivity with spread
      tasks = [...(data.tasks || [])];
      // Extract custom versions from tasks (only if not already in customVersions)
      tasks.forEach(t => {
        if (t.sprint && !INITIAL_VERSIONS.includes(t.sprint) && !customVersions.includes(t.sprint)) {
          customVersions = [...customVersions, t.sprint];
        }
      });
    } catch (err) {
      showToast(`Failed to load tasks: ${err.message}`, 'error');
      tasks = [];
    }
  }

  async function loadVersions() {
    try {
      const data = await fetchVersions();
      const loadedVersions = data.versions || [];

      // Build customVersions, hiddenDefaultVersions and versionLabels from backend
      const newCustomVersions = [];
      const newHiddenDefaults = [];
      const newVersionOrder = [];

      // Check for hidden default versions (stored with key like "_hidden_v1")
      loadedVersions.forEach(v => {
        if (v.key.startsWith('_hidden_')) {
          const hiddenKey = v.key.replace('_hidden_', '');
          newHiddenDefaults.push(hiddenKey);
        } else if (!INITIAL_VERSIONS.includes(v.key)) {
          newCustomVersions.push(v.key);
          versionLabels[v.key] = v.label;
          newVersionOrder.push(v.key);
        } else {
          // It's a default version with custom label
          versionLabels[v.key] = v.label;
          newVersionOrder.push(v.key);
        }
      });

      customVersions = newCustomVersions;
      hiddenDefaultVersions = newHiddenDefaults;
      versionLabels = { ...versionLabels };

      // Use loaded order if available, otherwise keep default
      if (newVersionOrder.length > 0) {
        // Ensure backlog is always last and filter out hidden versions
        const withoutBacklog = newVersionOrder.filter(v => v !== 'backlog' && !hiddenDefaultVersions.includes(v));
        versionOrder = [...withoutBacklog, 'backlog'];
      } else {
        // Filter hidden versions from default order
        versionOrder = versionOrder.filter(v => !hiddenDefaultVersions.includes(v));
      }
    } catch (err) {
      // Silently fail - versions will use defaults
      console.error('Failed to load versions:', err);
    }
  }

  // Generate a simple UUID
  function generateUUID() {
    return 'v-' + crypto.randomUUID();
  }

  // Version Management Functions
  async function handleAddVersion() {
    if (!newVersionName.trim()) {
      showToast('Please enter a version name', 'error');
      return;
    }
    const versionKey = generateUUID();

    // Calculate sort order (before backlog)
    const backlogIdx = versionOrder.indexOf('backlog');
    const sortOrder = backlogIdx >= 0 ? backlogIdx : versionOrder.length;

    try {
      await createVersion({
        key: versionKey,
        label: newVersionName.trim(),
        sort_order: sortOrder
      });

      customVersions = [...customVersions, versionKey];
      // Insert before backlog (which is always last)
      if (backlogIdx >= 0) {
        versionOrder = [...versionOrder.slice(0, backlogIdx), versionKey, ...versionOrder.slice(backlogIdx)];
      } else {
        versionOrder = [...versionOrder, versionKey];
      }
      versionLabels[versionKey] = newVersionName.trim();
      versionLabels = { ...versionLabels };
      newVersionName = '';
      showNewVersionInput = false;
      showToast('Version added', 'success');
    } catch (err) {
      showToast(`Failed to add version: ${err.message}`, 'error');
    }
  }

  function startEditVersion(version) {
    if (version === 'backlog') return; // Can't rename backlog
    editingVersion = version;
    editingVersionName = versionLabels[version] || version;
  }

  async function handleRenameVersion() {
    if (!editingVersionName.trim()) {
      showToast('Please enter a version name', 'error');
      return;
    }

    const versionKey = editingVersion;
    const newLabel = editingVersionName.trim();

    try {
      await updateVersion(versionKey, { label: newLabel });
      versionLabels[versionKey] = newLabel;
      versionLabels = { ...versionLabels };
      editingVersion = null;
      editingVersionName = '';
      showToast('Version renamed', 'success');
    } catch (err) {
      showToast(`Failed to rename version: ${err.message}`, 'error');
    }
  }

  function startDeleteVersion(version) {
    if (version === 'backlog') {
      showToast('Cannot delete Backlog', 'error');
      return;
    }
    deletingVersion = version;
    deleteTargetVersion = 'backlog';
  }

  async function confirmDeleteVersion() {
    if (!deletingVersion || isDeleting) return;

    const versionToDelete = deletingVersion;
    const targetVersion = deleteTargetVersion;
    const tasksCount = tasks.filter(t => (t.sprint || 'backlog') === versionToDelete).length;
    const isDefaultVersion = INITIAL_VERSIONS.includes(versionToDelete);

    isDeleting = true;

    try {
      // Call backend API to delete version and move tasks
      await deleteVersionApi(versionToDelete, targetVersion);

      // For default versions, we also need to store a "hidden" marker
      if (isDefaultVersion) {
        try {
          await createVersion({
            key: `_hidden_${versionToDelete}`,
            label: 'hidden',
            sort_order: -1
          });
        } catch (e) {
          // Ignore if already exists
        }
        hiddenDefaultVersions = [...hiddenDefaultVersions, versionToDelete];
      } else {
        customVersions = customVersions.filter(v => v !== versionToDelete);
      }

      // Update local state
      tasks = tasks.map(t => (t.sprint || 'backlog') === versionToDelete ? { ...t, sprint: targetVersion } : t);
      versionOrder = versionOrder.filter(v => v !== versionToDelete);
      delete versionLabels[versionToDelete];
      versionLabels = { ...versionLabels };

      showToast(`Version deleted. ${tasksCount} task(s) moved to ${getVersionLabel(targetVersion)}`, 'success');
    } catch (err) {
      showToast(`Failed to delete version: ${err.message}`, 'error');
    }

    isDeleting = false;
    deletingVersion = null;
    deleteTargetVersion = 'backlog';
  }

  function cancelDeleteVersion() {
    deletingVersion = null;
    deleteTargetVersion = 'backlog';
  }

  // Version reordering via drag
  function handleVersionDragStart(e, version) {
    if (version === 'backlog') {
      e.preventDefault();
      return;
    }
    draggedVersionItem = version;
    e.dataTransfer.effectAllowed = 'move';
  }

  function handleVersionDragOver(e, version) {
    e.preventDefault();
    if (draggedVersionItem && version !== draggedVersionItem) {
      dragOverVersionItem = version;
    }
  }

  async function handleVersionDrop(e, targetVersion) {
    e.preventDefault();
    if (!draggedVersionItem || draggedVersionItem === targetVersion) {
      draggedVersionItem = null;
      dragOverVersionItem = null;
      return;
    }

    // Reorder: remove dragged and insert before target
    const newOrder = versionOrder.filter(v => v !== draggedVersionItem);
    let targetIdx = newOrder.indexOf(targetVersion);

    // Ensure backlog always stays at the end
    const backlogIdx = newOrder.indexOf('backlog');
    if (targetIdx > backlogIdx) {
      targetIdx = backlogIdx;
    }

    newOrder.splice(targetIdx, 0, draggedVersionItem);
    versionOrder = newOrder;

    draggedVersionItem = null;
    dragOverVersionItem = null;

    // Persist to backend
    await saveVersionOrder(newOrder);
  }

  function handleVersionDragEnd() {
    draggedVersionItem = null;
    dragOverVersionItem = null;
  }

  async function moveVersionUp(version) {
    if (version === 'backlog') return; // Backlog can't move
    const idx = versionOrder.indexOf(version);
    if (idx <= 0) return; // Already at top
    const newOrder = [...versionOrder];
    [newOrder[idx - 1], newOrder[idx]] = [newOrder[idx], newOrder[idx - 1]];
    versionOrder = newOrder;

    // Persist to backend
    await saveVersionOrder(newOrder);
  }

  async function moveVersionDown(version) {
    if (version === 'backlog') return; // Backlog can't move
    const idx = versionOrder.indexOf(version);
    const backlogIdx = versionOrder.indexOf('backlog');
    // Can't move down if next item is backlog (backlog must stay last)
    if (idx >= backlogIdx - 1) return;
    const newOrder = [...versionOrder];
    [newOrder[idx], newOrder[idx + 1]] = [newOrder[idx + 1], newOrder[idx]];
    versionOrder = newOrder;

    // Persist to backend
    await saveVersionOrder(newOrder);
  }

  async function saveVersionOrder(order) {
    try {
      await reorderVersions(order);
    } catch (err) {
      console.error('Failed to save version order:', err);
    }
  }

  // Quick add task to specific version+status
  async function startQuickAdd(version, status) {
    quickAddVersion = version;
    quickAddStatus = status;
    quickAddTitle = '';
    await tick();
    if (quickAddInput) {
      quickAddInput.focus();
    }
  }

  function cancelQuickAdd() {
    quickAddVersion = null;
    quickAddStatus = null;
    quickAddTitle = '';
  }

  async function handleQuickAdd() {
    if (!quickAddTitle.trim() || isQuickAdding) {
      cancelQuickAdd();
      return;
    }

    isQuickAdding = true;
    const title = quickAddTitle.trim();
    const version = quickAddVersion;
    const status = quickAddStatus;

    // Clear quick add state
    cancelQuickAdd();

    try {
      const result = await createTask({
        title,
        description: '',
        status,
        sprint: version
      });
      // Handle API response - task may be in result.task or result directly
      const newTask = result.task || result;
      if (newTask && newTask.id) {
        tasks = [...tasks, newTask];
        showToast('Task created', 'success');
      } else {
        // Fallback: reload tasks from server
        await loadTasks();
        showToast('Task created', 'success');
      }
    } catch (err) {
      showToast(`Failed to create task: ${err.message}`, 'error');
      await loadTasks();
    } finally {
      isQuickAdding = false;
    }
  }

  async function handleAddTask() {
    if (!newTaskTitle.trim()) {
      showToast('Please enter a task title', 'error');
      return;
    }

    const title = newTaskTitle.trim();
    const description = newTaskDescription.trim();
    const version = newTaskVersion;

    // Clear fields and close modal
    newTaskTitle = '';
    newTaskDescription = '';
    newTaskVersion = 'backlog';
    showAddModal = false;

    try {
      const result = await createTask({
        title,
        description,
        status: 'todo',
        sprint: version // Backend uses 'sprint' field
      });
      // Handle API response - task may be in result.task or result directly
      const newTask = result.task || result;
      if (newTask && newTask.id) {
        tasks = [...tasks, newTask];
        showToast('Task created', 'success');
      } else {
        // Fallback: reload tasks from server
        await loadTasks();
        showToast('Task created', 'success');
      }
    } catch (err) {
      showToast(`Failed to create task: ${err.message}`, 'error');
      // Reload to sync state
      await loadTasks();
    }
  }

  async function handleStatusChange(task, newStatus) {
    const oldStatus = task.status;
    // Optimistic update
    tasks = tasks.map(t => t.id === task.id ? { ...t, status: newStatus } : t);

    try {
      await updateTask(task.id, { status: newStatus });
    } catch (err) {
      // Revert on error
      tasks = tasks.map(t => t.id === task.id ? { ...t, status: oldStatus } : t);
      showToast(`Failed to update task: ${err.message}`, 'error');
    }
  }

  async function handleVersionChange(task, newVersion) {
    const oldVersion = task.sprint;
    // Optimistic update
    tasks = tasks.map(t => t.id === task.id ? { ...t, sprint: newVersion } : t);

    try {
      await updateTask(task.id, { sprint: newVersion });
    } catch (err) {
      // Revert on error
      tasks = tasks.map(t => t.id === task.id ? { ...t, sprint: oldVersion } : t);
      showToast(`Failed to update task: ${err.message}`, 'error');
    }
  }

  function handleDeleteTask(task) {
    deletingTask = task;
  }

  async function confirmDeleteTask() {
    if (!deletingTask) return;

    const taskToDelete = deletingTask;
    const oldTasks = [...tasks];

    // Close modals
    deletingTask = null;
    if (viewingTask?.id === taskToDelete.id) {
      viewingTask = null;
      editingTask = null;
    }

    // Optimistic delete
    tasks = tasks.filter(t => t.id !== taskToDelete.id);

    try {
      await deleteTask(taskToDelete.id);
      showToast('Task deleted', 'success');
    } catch (err) {
      // Revert on error
      tasks = oldTasks;
      showToast(`Failed to delete task: ${err.message}`, 'error');
    }
  }

  function cancelDeleteTask() {
    deletingTask = null;
  }

  async function handleCopyTask(task) {
    const json = JSON.stringify({
      task_id: task.id,
      title: task.title,
      description: task.description || ''
    }, null, 2);

    try {
      await navigator.clipboard.writeText(json);
      copiedTaskId = task.id;
      copiedWithPlan = false;
      setTimeout(() => copiedTaskId = null, 2000);
    } catch (err) {
      showToast('Failed to copy to clipboard', 'error');
    }
  }

  async function handleCopyTaskWithPlan(task) {
    const prompt = `## Task
${task.title}

${task.description || ''}

---

Please help me implement this task:

1. **Deep Plan**: Before writing any code, create a detailed implementation plan. Consider:
   - What files need to be created or modified
   - What components/functions are needed
   - What edge cases to handle
   - What dependencies or imports are required
   - The order of implementation steps

2. **Implementation**: After I approve the plan, implement the solution step by step.

3. **Tests**: Write comprehensive tests covering:
   - Happy path scenarios
   - Edge cases
   - Error handling
   - Integration with existing code

Task ID: ${task.id}`;

    try {
      await navigator.clipboard.writeText(prompt);
      copiedTaskId = task.id;
      copiedWithPlan = true;
      setTimeout(() => { copiedTaskId = null; copiedWithPlan = false; }, 2000);
    } catch (err) {
      showToast('Failed to copy to clipboard', 'error');
    }
  }

  async function handleSaveEdit() {
    if (!editingTask || !editingTask.title.trim()) {
      showToast('Please enter a task title', 'error');
      return;
    }

    const updatedTask = {
      ...editingTask,
      title: editingTask.title.trim(),
      description: editingTask.description.trim()
    };
    const taskId = editingTask.id;
    const oldTasks = [...tasks];

    // Optimistic update
    tasks = tasks.map(t => t.id === taskId ? updatedTask : t);
    editingTask = null;

    try {
      await updateTask(taskId, {
        title: updatedTask.title,
        description: updatedTask.description,
        sprint: updatedTask.sprint
      });
      showToast('Task updated', 'success');
    } catch (err) {
      tasks = oldTasks;
      showToast(`Failed to update task: ${err.message}`, 'error');
    }
  }

  // Drag and drop handlers
  function handleDragStart(e, task) {
    draggedTask = task;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', task.id);

    // Create tilted drag image
    const dragImage = e.target.cloneNode(true);
    dragImage.style.position = 'absolute';
    dragImage.style.top = '-1000px';
    dragImage.style.transform = 'rotate(-3deg) scale(1.02)';
    dragImage.style.boxShadow = '0 10px 30px rgba(0,0,0,0.25)';
    dragImage.style.opacity = '0.9';
    dragImage.style.pointerEvents = 'none';
    dragImage.style.width = e.target.offsetWidth + 'px';
    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, e.target.offsetWidth / 2, 20);

    // Clean up after drag starts
    setTimeout(() => {
      document.body.removeChild(dragImage);
    }, 0);
  }

  function handleDragEnd() {
    draggedTask = null;
    dragOverColumn = null;
    dragOverVersion = null;
    dragOverTaskId = null;
  }

  function handleDragOver(e, status, version = null) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    dragOverColumn = status;
    dragOverVersion = version;
  }

  function handleDragLeave() {
    dragOverColumn = null;
    dragOverVersion = null;
  }

  function handleTaskDragOver(e, task) {
    e.preventDefault();
    e.stopPropagation();
    if (draggedTask && draggedTask.id !== task.id) {
      dragOverTaskId = task.id;
    }
  }

  function handleTaskDragLeave(e) {
    // Only clear if we're leaving the task card entirely
    const relatedTarget = e.relatedTarget;
    if (!relatedTarget || !e.currentTarget.contains(relatedTarget)) {
      dragOverTaskId = null;
    }
  }

  // Handle drop directly on a task card (for reordering)
  async function handleTaskDrop(e, targetTask, status, version) {
    e.preventDefault();
    e.stopPropagation();

    dragOverColumn = null;
    dragOverVersion = null;
    dragOverTaskId = null;

    if (!draggedTask || draggedTask.id === targetTask.id) {
      draggedTask = null;
      return;
    }

    const taskVersion = version !== null ? version : (draggedTask.sprint || 'backlog');
    const targetVersion = targetTask.sprint || 'backlog';
    const sameColumn = draggedTask.status === status && (draggedTask.sprint || 'backlog') === taskVersion;

    if (sameColumn) {
      // Reorder within same column
      await handleTaskReorder(draggedTask, targetTask.id, status, taskVersion);
    } else {
      // Move to different column and place before target
      const updates = { status, sprint: version };
      const oldTask = { ...draggedTask };

      tasks = tasks.map(t => t.id === draggedTask.id ? { ...t, ...updates } : t);

      try {
        await updateTask(draggedTask.id, updates);
        // After moving, reorder to place before target
        await handleTaskReorder({ ...draggedTask, ...updates }, targetTask.id, status, version);
      } catch (err) {
        tasks = tasks.map(t => t.id === draggedTask.id ? oldTask : t);
        showToast(`Failed to move task: ${err.message}`, 'error');
      }
    }

    draggedTask = null;
  }

  async function handleDrop(e, status, version = null) {
    e.preventDefault();
    dragOverColumn = null;
    dragOverVersion = null;
    dragOverTaskId = null;

    if (!draggedTask) return;

    const taskVersion = version !== null ? version : (draggedTask.sprint || 'backlog');
    const sameColumn = draggedTask.status === status && (draggedTask.sprint || 'backlog') === taskVersion;

    // If same column with no target task, do nothing (task stays in place)
    if (sameColumn) {
      draggedTask = null;
      return;
    }

    const updates = {};
    if (draggedTask.status !== status) {
      updates.status = status;
    }
    if (version !== null && (draggedTask.sprint || 'backlog') !== version) {
      updates.sprint = version;
    }

    if (Object.keys(updates).length === 0) {
      draggedTask = null;
      return;
    }

    const oldTask = { ...draggedTask };

    // Optimistic update
    tasks = tasks.map(t => t.id === draggedTask.id ? { ...t, ...updates } : t);

    try {
      await updateTask(draggedTask.id, updates);
    } catch (err) {
      // Revert on error
      tasks = tasks.map(t => t.id === draggedTask.id ? oldTask : t);
      showToast(`Failed to move task: ${err.message}`, 'error');
    }

    draggedTask = null;
  }

  async function handleTaskReorder(movedTask, targetTaskId, status, version) {
    // Get tasks in this column, sorted by current sort_order
    const columnTasks = tasks
      .filter(t => t.status === status && (t.sprint || 'backlog') === version)
      .sort((a, b) => (a.sort_order ?? 999999) - (b.sort_order ?? 999999));

    // Find indices
    const movedIdx = columnTasks.findIndex(t => t.id === movedTask.id);
    const targetIdx = columnTasks.findIndex(t => t.id === targetTaskId);

    if (movedIdx === -1 || targetIdx === -1) return;

    // Remove moved task and insert before target
    const newOrder = [...columnTasks];
    newOrder.splice(movedIdx, 1);
    const insertIdx = targetIdx > movedIdx ? targetIdx - 1 : targetIdx;
    newOrder.splice(insertIdx, 0, movedTask);

    // Get new task IDs order for this column
    const taskIds = newOrder.map(t => t.id);

    // Optimistic update - update sort_order for all tasks in this column
    tasks = tasks.map(t => {
      const idx = taskIds.indexOf(t.id);
      if (idx !== -1) {
        return { ...t, sort_order: idx };
      }
      return t;
    });

    try {
      await reorderTasks(taskIds);
    } catch (err) {
      showToast(`Failed to reorder tasks: ${err.message}`, 'error');
      await loadTasks(); // Reload to restore correct order
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      if (deletingTask) {
        cancelDeleteTask();
      } else if (deletingVersion) {
        cancelDeleteVersion();
      } else if (showVersionsMenu) {
        showVersionsMenu = false;
        showNewVersionInput = false;
        editingVersion = null;
      } else if (showAddModal) {
        showAddModal = false;
      } else if (viewingTask) {
        viewingTask = null;
        editingTask = null;
      } else if (editingTask) {
        editingTask = null;
      } else if (!inline) {
        onClose();
      }
    }
  }

  function handleClickOutside(e) {
    if (showVersionsMenu) {
      const container = e.target.closest('.versions-menu-container');
      if (!container) {
        showVersionsMenu = false;
        showNewVersionInput = false;
        editingVersion = null;
      }
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} on:click={handleClickOutside} />

{#if inline}
  <!-- Inline mode: no backdrop, fills container -->
  <div class="task-manager-inline">
    <div class="panel-header">
      <div class="header-left-section">
        <div class="versions-menu-container">
          <button class="versions-menu-btn" on:click={() => showVersionsMenu = !showVersionsMenu}>
            {allVersionsVisible ? 'All Versions' : `${visibleVersions.size} Version${visibleVersions.size === 1 ? '' : 's'}`}
            <span class="chevron">{showVersionsMenu ? '▲' : '▼'}</span>
          </button>
          {#if showVersionsMenu}
            <div class="versions-dropdown" on:click|stopPropagation>
              <div class="versions-list">
                <label class="version-item version-checkbox-item">
                  <input
                    type="checkbox"
                    checked={allVersionsVisible}
                    on:change={toggleAllVersions}
                  />
                  <span class="version-name">All Versions</span>
                  <span class="version-task-count">{tasks.length}</span>
                </label>
                {#each versions as version, idx (version)}
                  <div
                    class="version-item"
                    class:drag-over={dragOverVersionItem === version}
                    class:is-backlog={version === 'backlog'}
                    draggable={version !== 'backlog'}
                    on:dragstart={(e) => handleVersionDragStart(e, version)}
                    on:dragover={(e) => handleVersionDragOver(e, version)}
                    on:drop={(e) => handleVersionDrop(e, version)}
                    on:dragend={handleVersionDragEnd}
                  >
                    {#if editingVersion === version}
                      <input
                        class="version-edit-input"
                        bind:value={editingVersionName}
                        on:click|stopPropagation
                        on:keydown={(e) => {
                          if (e.key === 'Enter') handleRenameVersion();
                          if (e.key === 'Escape') { editingVersion = null; editingVersionName = ''; }
                        }}
                        on:blur={handleRenameVersion}
                      />
                    {:else}
                      <label class="version-checkbox-label">
                        <input
                          type="checkbox"
                          checked={isVersionVisible(version)}
                          on:change={() => toggleVersionVisibility(version)}
                        />
                        <span class="version-name">{getVersionLabel(version)}</span>
                        <span class="version-task-count">{tasks.filter(t => (t.sprint || 'backlog') === version).length}</span>
                      </label>
                      <div class="version-actions">
                        {#if version !== 'backlog'}
                          <button class="version-action-btn" on:click|stopPropagation={() => moveVersionUp(version)} title="Move up" disabled={idx === 0}>↑</button>
                          <button class="version-action-btn" on:click|stopPropagation={() => moveVersionDown(version)} title="Move down" disabled={idx >= versions.indexOf('backlog') - 1}>↓</button>
                          <button class="version-action-btn" on:click|stopPropagation={() => startEditVersion(version)} title="Rename">✎</button>
                          <button class="version-action-btn delete" on:click|stopPropagation={() => startDeleteVersion(version)} title="Delete">×</button>
                        {/if}
                      </div>
                    {/if}
                  </div>
                {/each}
              </div>
              <div class="versions-add-section">
                {#if showNewVersionInput}
                  <div class="new-version-row">
                    <input
                      class="new-version-input-field"
                      type="text"
                      bind:value={newVersionName}
                      placeholder="Version name"
                      on:keydown={(e) => {
                        if (e.key === 'Enter') handleAddVersion();
                        if (e.key === 'Escape') { showNewVersionInput = false; newVersionName = ''; }
                      }}
                    />
                    <button class="small-btn" on:click|stopPropagation={handleAddVersion}>Add</button>
                    <button class="small-btn cancel" on:click|stopPropagation={() => { showNewVersionInput = false; newVersionName = ''; }}>×</button>
                  </div>
                {:else}
                  <button class="add-version-in-menu" on:click|stopPropagation={() => showNewVersionInput = true}>+ Add Version</button>
                {/if}
              </div>
            </div>
          {/if}
        </div>
      </div>
      <div class="header-actions">
        <div class="view-toggle">
          <button
            class="view-btn"
            class:active={viewMode === 'kanban'}
            on:click={() => viewMode = 'kanban'}
          >
            Kanban
          </button>
          <button
            class="view-btn"
            class:active={viewMode === 'list'}
            on:click={() => viewMode = 'list'}
          >
            List
          </button>
        </div>
      </div>
    </div>

    <div class="panel-content">
      {#if loading}
        <div class="loading">Loading...</div>
      {:else if viewMode === 'kanban'}
        <!-- Version Swim Lanes View -->
        <div class="swim-lanes">
          {#each filteredSwimLaneData as lane (lane.version)}
              {#if lane.tasks.length > 0 || lane.isDefault || lane.isCustom}
                <div class="swim-lane" class:collapsed={collapsedVersions.has(lane.version)}>
                  <div class="swim-lane-header" on:click={() => toggleCollapse(lane.version)} role="button" tabindex="0" on:keydown={(e) => e.key === 'Enter' && toggleCollapse(lane.version)}>
                    <span class="collapse-icon">
                      {#if collapsedVersions.has(lane.version)}
                        <ChevronRight size={14} />
                      {:else}
                        <ChevronDown size={14} />
                      {/if}
                    </span>
                    <span class="swim-lane-title">{lane.label}</span>
                    <span class="swim-lane-count">{lane.tasks.length} tasks</span>
                  </div>
                  {#if !collapsedVersions.has(lane.version)}
                  <div class="kanban-board">
                    {#each STATUSES as status}
                      {@const columnTasks = lane.byStatus[status]}
                      <div
                        class="kanban-column"
                        class:drag-over={dragOverColumn === status && dragOverVersion === lane.version}
                        on:dragover={(e) => handleDragOver(e, status, lane.version)}
                        on:dragleave={handleDragLeave}
                        on:drop={(e) => handleDrop(e, status, lane.version)}
                        role="list"
                      >
                        <div class="column-header">
                          <span class="column-title">{STATUS_LABELS[status]}</span>
                          <div class="column-header-right">
                            <span class="column-count">{columnTasks.length}</span>
                            <button
                              class="quick-add-btn"
                              on:click={() => startQuickAdd(lane.version, status)}
                              title="Add task"
                            >+</button>
                          </div>
                        </div>
                        <div class="column-tasks">
                          {#if quickAddVersion === lane.version && quickAddStatus === status}
                            <div class="quick-add-card">
                              <input
                                bind:this={quickAddInput}
                                bind:value={quickAddTitle}
                                class="quick-add-input"
                                placeholder="Task title... (Enter to save)"
                                on:keydown={(e) => {
                                  if (e.key === 'Enter') handleQuickAdd();
                                  if (e.key === 'Escape') cancelQuickAdd();
                                }}
                                on:blur={() => { if (!quickAddTitle.trim()) cancelQuickAdd(); }}
                              />
                            </div>
                          {/if}
                          {#each columnTasks as task (task.id)}
                            <div
                              class="task-card"
                              class:dragging={draggedTask?.id === task.id}
                              class:drag-over-task={dragOverTaskId === task.id}
                              draggable="true"
                              on:dragstart={(e) => handleDragStart(e, task)}
                              on:dragend={handleDragEnd}
                              on:dragover={(e) => handleTaskDragOver(e, task)}
                              on:dragleave={handleTaskDragLeave}
                              on:drop={(e) => handleTaskDrop(e, task, status, lane.version)}
                              on:click={() => { viewingTask = { ...task }; editingTask = { ...task }; }}
                              role="listitem"
                            >
                              <div class="task-title">{task.title}</div>
                              {#if task.description}
                                <div class="task-description">{task.description}</div>
                              {/if}
                              <div class="task-actions">
                                <button
                                  class="copy-btn"
                                  on:click|stopPropagation={() => handleCopyTask(task)}
                                  title="Copy"
                                >⧉</button>
                                <button
                                  class="delete-btn"
                                  on:click|stopPropagation={() => handleDeleteTask(task)}
                                  title="Delete"
                                >×</button>
                              </div>
                            </div>
                          {/each}
                          {#if columnTasks.length === 0 && !(quickAddVersion === lane.version && quickAddStatus === status)}
                            <div class="empty-column" on:click={() => startQuickAdd(lane.version, status)} role="button" tabindex="0" on:keydown={(e) => e.key === 'Enter' && startQuickAdd(lane.version, status)}>Click to add task</div>
                          {/if}
                        </div>
                      </div>
                    {/each}
                  </div>
                  {/if}
                </div>
              {/if}
            {/each}
          </div>
      {:else}
        <div class="list-view">
          <table class="task-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Description</th>
                <th>Version</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each tasks as task (task.id)}
                <tr>
                  <td>{task.title}</td>
                  <td class="description-cell">{task.description || '-'}</td>
                  <td>
                    <select
                      class="version-select"
                      value={task.sprint || 'backlog'}
                      on:change={(e) => handleVersionChange(task, e.target.value)}
                    >
                      {#each versions as v}
                        <option value={v}>{getVersionLabel(v)}</option>
                      {/each}
                    </select>
                  </td>
                  <td>
                    <select
                      class="status-select"
                      value={task.status}
                      on:change={(e) => handleStatusChange(task, e.target.value)}
                    >
                      {#each STATUSES as s}
                        <option value={s}>{STATUS_LABELS[s]}</option>
                      {/each}
                    </select>
                  </td>
                  <td>
                    <button
                      class="edit-btn"
                      on:click={() => editingTask = { ...task }}
                    >
                      Edit
                    </button>
                    <button
                      class="delete-btn"
                      on:click={() => handleDeleteTask(task)}
                    >
                      X
                    </button>
                  </td>
                </tr>
              {/each}
              {#if tasks.length === 0}
                <tr>
                  <td colspan="5" class="empty-table">No tasks yet. Click "Add Task" to create one.</td>
                </tr>
              {/if}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  </div>
{:else}
  <!-- Modal mode: with backdrop -->
  <div class="task-manager-backdrop" on:click={onClose} role="dialog">
    <div class="task-manager-panel" on:click|stopPropagation role="document">
      <div class="panel-header">
        <h3>Tasks</h3>
        <div class="header-actions">
          <div class="versions-menu-container">
            <button class="versions-menu-btn" on:click={() => showVersionsMenu = !showVersionsMenu}>
              {allVersionsVisible ? 'All Versions' : `${visibleVersions.size} Version${visibleVersions.size === 1 ? '' : 's'}`}
              <span class="chevron">{showVersionsMenu ? '▲' : '▼'}</span>
            </button>
            {#if showVersionsMenu}
              <div class="versions-dropdown" on:click|stopPropagation>
                <div class="versions-list">
                  <label class="version-item version-checkbox-item">
                    <input
                      type="checkbox"
                      checked={allVersionsVisible}
                      on:change={toggleAllVersions}
                    />
                    <span class="version-name">All Versions</span>
                    <span class="version-task-count">{tasks.length}</span>
                  </label>
                  {#each versions as version (version)}
                    <label class="version-item version-checkbox-item">
                      <input
                        type="checkbox"
                        checked={isVersionVisible(version)}
                        on:change={() => toggleVersionVisibility(version)}
                      />
                      <span class="version-name">{getVersionLabel(version)}</span>
                      <span class="version-task-count">{tasks.filter(t => (t.sprint || 'backlog') === version).length}</span>
                    </label>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
          <div class="view-toggle">
            <button
              class="view-btn"
              class:active={viewMode === 'kanban'}
              on:click={() => viewMode = 'kanban'}
            >
              Kanban
            </button>
            <button
              class="view-btn"
              class:active={viewMode === 'list'}
              on:click={() => viewMode = 'list'}
            >
              List
            </button>
          </div>
          <button class="close-btn" on:click={onClose}>X</button>
        </div>
      </div>

      <div class="panel-content">
        {#if loading}
          <div class="loading">Loading...</div>
        {:else if viewMode === 'kanban'}
          <!-- Version Swim Lanes View -->
          <div class="swim-lanes">
            {#each filteredSwimLaneData as lane (lane.version)}
                {#if lane.tasks.length > 0 || lane.isDefault || lane.isCustom}
                  <div class="swim-lane" class:collapsed={collapsedVersions.has(lane.version)}>
                    <div class="swim-lane-header" on:click={() => toggleCollapse(lane.version)} role="button" tabindex="0" on:keydown={(e) => e.key === 'Enter' && toggleCollapse(lane.version)}>
                      <span class="collapse-icon">
                        {#if collapsedVersions.has(lane.version)}
                          <ChevronRight size={14} />
                        {:else}
                          <ChevronDown size={14} />
                        {/if}
                      </span>
                      <span class="swim-lane-title">{lane.label}</span>
                      <span class="swim-lane-count">{lane.tasks.length} tasks</span>
                    </div>
                    {#if !collapsedVersions.has(lane.version)}
                    <div class="kanban-board">
                      {#each STATUSES as status}
                        {@const columnTasks = lane.byStatus[status]}
                        <div
                          class="kanban-column"
                          class:drag-over={dragOverColumn === status && dragOverVersion === lane.version}
                          on:dragover={(e) => handleDragOver(e, status, lane.version)}
                          on:dragleave={handleDragLeave}
                          on:drop={(e) => handleDrop(e, status, lane.version)}
                          role="list"
                        >
                          <div class="column-header">
                            <span class="column-title">{STATUS_LABELS[status]}</span>
                            <span class="column-count">{columnTasks.length}</span>
                          </div>
                          <div class="column-tasks">
                            {#each columnTasks as task (task.id)}
                              <div
                                class="task-card"
                                class:dragging={draggedTask?.id === task.id}
                                class:drag-over-task={dragOverTaskId === task.id}
                                draggable="true"
                                on:dragstart={(e) => handleDragStart(e, task)}
                                on:dragend={handleDragEnd}
                                on:dragover={(e) => handleTaskDragOver(e, task)}
                                on:dragleave={handleTaskDragLeave}
                                on:drop={(e) => handleTaskDrop(e, task, status, lane.version)}
                                on:click={() => { viewingTask = { ...task }; editingTask = { ...task }; }}
                                role="listitem"
                              >
                                <div class="task-title">{task.title}</div>
                                {#if task.description}
                                  <div class="task-description">{task.description}</div>
                                {/if}
                                <div class="task-actions">
                                  <button
                                    class="copy-btn"
                                    on:click|stopPropagation={() => handleCopyTask(task)}
                                    title="Copy"
                                  >⧉</button>
                                  <button
                                    class="delete-btn"
                                    on:click|stopPropagation={() => handleDeleteTask(task)}
                                    title="Delete"
                                  >×</button>
                                </div>
                              </div>
                            {/each}
                            {#if columnTasks.length === 0}
                              <div class="empty-column">Drop here</div>
                            {/if}
                          </div>
                        </div>
                      {/each}
                    </div>
                    {/if}
                  </div>
                {/if}
              {/each}
            </div>
        {:else}
          <div class="list-view">
            <table class="task-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Description</th>
                  <th>Version</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {#each tasks as task (task.id)}
                  <tr>
                    <td>{task.title}</td>
                    <td class="description-cell">{task.description || '-'}</td>
                    <td>
                      <select
                        class="version-select"
                        value={task.sprint || 'backlog'}
                        on:change={(e) => handleVersionChange(task, e.target.value)}
                      >
                        {#each versions as v}
                          <option value={v}>{getVersionLabel(v)}</option>
                        {/each}
                      </select>
                    </td>
                    <td>
                      <select
                        class="status-select"
                        value={task.status}
                        on:change={(e) => handleStatusChange(task, e.target.value)}
                      >
                        {#each STATUSES as s}
                          <option value={s}>{STATUS_LABELS[s]}</option>
                        {/each}
                      </select>
                    </td>
                    <td>
                      <button
                        class="edit-btn"
                        on:click={() => editingTask = { ...task }}
                      >
                        Edit
                      </button>
                      <button
                        class="delete-btn"
                        on:click={() => handleDeleteTask(task)}
                      >
                        X
                      </button>
                    </td>
                  </tr>
                {/each}
                {#if tasks.length === 0}
                  <tr>
                    <td colspan="5" class="empty-table">No tasks yet. Click "Add Task" to create one.</td>
                  </tr>
                {/if}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<!-- Add Task Modal -->
{#if showAddModal}
  <div class="modal-backdrop" on:click={() => showAddModal = false} role="dialog">
    <div class="modal" on:click|stopPropagation role="document">
      <div class="modal-header">
        <h4>Add Task</h4>
        <button class="close-btn" on:click={() => showAddModal = false}>X</button>
      </div>
      <div class="modal-body">
        <input
          class="input-field"
          bind:value={newTaskTitle}
          placeholder="Task title"
          on:keydown={(e) => e.key === 'Enter' && handleAddTask()}
        />
        <textarea
          class="textarea-field"
          bind:value={newTaskDescription}
          placeholder="Description (optional)"
          rows="3"
        ></textarea>
        <select class="select-field" bind:value={newTaskVersion}>
          {#each versions as v}
            <option value={v}>{getVersionLabel(v)}</option>
          {/each}
        </select>
      </div>
      <div class="modal-footer">
        <button class="action-btn primary" on:click={handleAddTask}>Add Task</button>
        <button class="action-btn" on:click={() => showAddModal = false}>Cancel</button>
      </div>
    </div>
  </div>
{/if}

<!-- Edit Task Modal (for list view) -->
{#if editingTask && viewMode === 'list'}
  <div class="modal-backdrop" on:click={() => editingTask = null} role="dialog">
    <div class="modal" on:click|stopPropagation role="document">
      <div class="modal-header">
        <h4>Edit Task</h4>
        <button class="close-btn" on:click={() => editingTask = null}>X</button>
      </div>
      <div class="modal-body">
        <input
          class="input-field"
          bind:value={editingTask.title}
          placeholder="Task title"
        />
        <textarea
          class="textarea-field"
          bind:value={editingTask.description}
          placeholder="Description (optional)"
          rows="3"
        ></textarea>
        <select class="select-field" bind:value={editingTask.sprint}>
          {#each versions as v}
            <option value={v}>{getVersionLabel(v)}</option>
          {/each}
        </select>
      </div>
      <div class="modal-footer">
        <button class="action-btn primary" on:click={handleSaveEdit}>Save</button>
        <button class="action-btn" on:click={() => editingTask = null}>Cancel</button>
      </div>
    </div>
  </div>
{/if}

<!-- Delete Version Confirmation Modal -->
{#if deletingVersion}
  <div class="modal-backdrop" on:click={cancelDeleteVersion} role="dialog">
    <div class="modal delete-version-modal" on:click|stopPropagation role="document">
      <div class="modal-header">
        <h4>Delete Version</h4>
        <button class="close-btn" on:click={cancelDeleteVersion}>X</button>
      </div>
      <div class="modal-body">
        <p class="delete-warning">
          Are you sure you want to delete <strong>{getVersionLabel(deletingVersion)}</strong>?
        </p>
        {#if tasks.filter(t => (t.sprint || 'backlog') === deletingVersion).length > 0}
          <p class="reassign-info">
            {tasks.filter(t => (t.sprint || 'backlog') === deletingVersion).length} task{tasks.filter(t => (t.sprint || 'backlog') === deletingVersion).length > 1 ? 's' : ''} will be moved to:
          </p>
          <select class="select-field" bind:value={deleteTargetVersion}>
            {#each versions.filter(v => v !== deletingVersion) as v}
              <option value={v}>{getVersionLabel(v)}</option>
            {/each}
          </select>
        {:else}
          <p class="no-tasks-info">This version has no tasks.</p>
        {/if}
      </div>
      <div class="modal-footer">
        <button class="action-btn danger" on:click={confirmDeleteVersion} disabled={isDeleting}>
          {#if isDeleting}
            <span class="spinner"></span> Deleting...
          {:else}
            Delete Version
          {/if}
        </button>
        <button class="action-btn" on:click={cancelDeleteVersion} disabled={isDeleting}>Cancel</button>
      </div>
    </div>
  </div>
{/if}

<!-- Delete Task Confirmation Modal -->
{#if deletingTask}
  <div class="modal-backdrop" on:click={cancelDeleteTask} role="dialog">
    <div class="modal delete-task-modal" on:click|stopPropagation role="document">
      <div class="modal-header">
        <h4>Delete Task</h4>
        <button class="close-btn" on:click={cancelDeleteTask}>×</button>
      </div>
      <div class="modal-body">
        <p class="delete-warning">
          Are you sure you want to delete this task?
        </p>
        <div class="delete-task-preview">
          <div class="delete-task-title">{deletingTask.title}</div>
          {#if deletingTask.description}
            <div class="delete-task-description">{deletingTask.description}</div>
          {/if}
        </div>
      </div>
      <div class="modal-footer">
        <button class="action-btn danger" on:click={confirmDeleteTask}>Delete Task</button>
        <button class="action-btn" on:click={cancelDeleteTask}>Cancel</button>
      </div>
    </div>
  </div>
{/if}

<!-- Task Detail Modal -->
{#if viewingTask}
  <div class="modal-backdrop task-detail-backdrop" on:click={() => { viewingTask = null; editingTask = null; }} role="dialog">
    <div class="task-detail-modal" on:click|stopPropagation role="document">
      <div class="task-detail-header">
        <div class="task-detail-meta">
          <span class="task-detail-status status-{viewingTask.status}">{STATUS_LABELS[viewingTask.status]}</span>
          <span class="task-detail-version">{getVersionLabel(viewingTask.sprint || 'backlog')}</span>
        </div>
        <button class="close-btn" on:click={() => { viewingTask = null; editingTask = null; }}>×</button>
      </div>

      <div class="task-detail-body">
        {#if editingTask}
          <input
            class="task-detail-title-input"
            bind:value={editingTask.title}
            placeholder="Task title"
          />
          <textarea
            class="task-detail-description-input"
            bind:value={editingTask.description}
            placeholder="Add a description..."
            rows="6"
          ></textarea>

          <div class="task-detail-fields">
            <div class="task-detail-field">
              <label>Status</label>
              <select bind:value={editingTask.status}>
                {#each STATUSES as s}
                  <option value={s}>{STATUS_LABELS[s]}</option>
                {/each}
              </select>
            </div>
            <div class="task-detail-field">
              <label>Version</label>
              <select bind:value={editingTask.sprint}>
                {#each versions as v}
                  <option value={v}>{getVersionLabel(v)}</option>
                {/each}
              </select>
            </div>
          </div>
        {:else}
          <h2 class="task-detail-title">{viewingTask.title}</h2>
          <div class="task-detail-description">
            {#if viewingTask.description}
              {viewingTask.description}
            {:else}
              <span class="no-description">No description</span>
            {/if}
          </div>
        {/if}
      </div>

      <div class="task-detail-footer">
        <div class="footer-left">
          <button class="action-btn" on:click={() => handleCopyTask(editingTask || viewingTask)}>
            {copiedTaskId === (editingTask || viewingTask)?.id && !copiedWithPlan ? 'Copied!' : 'Copy for AI'}
          </button>
          <button class="action-btn" on:click={() => handleCopyTaskWithPlan(editingTask || viewingTask)}>
            {copiedTaskId === (editingTask || viewingTask)?.id && copiedWithPlan ? 'Copied!' : 'Copy + Plan + Tests'}
          </button>
        </div>
        <div class="footer-right">
          {#if editingTask}
            <button class="action-btn primary" on:click={async () => { await handleSaveEdit(); viewingTask = tasks.find(t => t.id === editingTask?.id) || null; editingTask = null; }}>Save</button>
            <button class="action-btn" on:click={() => editingTask = null}>Cancel</button>
          {:else}
            <button class="action-btn" on:click={() => editingTask = { ...viewingTask }}>Edit</button>
            <button class="action-btn danger" on:click={() => handleDeleteTask(viewingTask)}>Delete</button>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Inline mode styles */
  .task-manager-inline {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary);
  }

  .task-manager-inline .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    background: transparent;
  }

  .task-manager-inline .panel-content {
    flex: 1;
    overflow: auto;
    padding: 0 20px 20px 20px;
  }

  .header-left-section {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  /* Modal mode styles */
  .task-manager-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(2px);
  }

  .task-manager-panel {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    width: 95%;
    max-width: 1400px;
    height: 85vh;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-large);
  }

  .task-manager-panel .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-secondary);
  }

  .task-manager-panel .panel-header h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-primary);
  }

  .task-manager-panel .panel-content {
    flex: 1;
    overflow: auto;
    padding: 20px;
  }

  .header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .version-toggle {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 10px;
    color: var(--text-secondary);
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .version-toggle input {
    cursor: pointer;
  }

  .view-toggle {
    display: flex;
    gap: 4px;
  }

  .view-btn {
    padding: 4px 8px;
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 10px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.15s;
    border-radius: 3px;
  }

  .view-btn:hover {
    color: var(--text-secondary);
    background: var(--bg-hover);
  }

  .view-btn.active {
    color: var(--text-primary);
    background: var(--bg-primary);
  }

  .add-btn {
    padding: 6px 12px;
    background: var(--accent-primary);
    color: var(--bg-primary);
    border: none;
    border-radius: 1px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .add-btn:hover {
    opacity: 0.9;
  }

  .close-btn {
    padding: 6px 10px;
    background: transparent;
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    border-radius: 1px;
    font-size: 10px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .close-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: var(--text-secondary);
  }

  /* Swim Lanes */
  .swim-lanes {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .swim-lane {
    background: transparent;
  }

  .swim-lane-header {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-bottom: 1px solid var(--border-secondary);
    margin-bottom: 12px;
    cursor: pointer;
    user-select: none;
    border-radius: 4px;
  }

  .swim-lane-header:hover {
    background: var(--bg-hover);
  }

  .swim-lane.collapsed .swim-lane-header {
    margin-bottom: 0;
    border-bottom: none;
  }

  .swim-lane-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-secondary);
  }

  .collapse-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-tertiary);
  }

  .swim-lane-count {
    font-size: 10px;
    color: var(--text-tertiary);
  }

  /* Kanban View */
  .kanban-board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    padding: 0;
  }

  .kanban-board.full-height {
    height: 100%;
    padding: 0;
  }

  .kanban-column {
    background: transparent;
    border: none;
    display: flex;
    flex-direction: column;
    min-height: 150px;
    min-width: 0;
    overflow: hidden;
    transition: background 0.2s;
  }

  .kanban-column.drag-over {
    background: rgba(255, 255, 255, 0.02);
  }

  .full-height .kanban-column {
    min-height: 300px;
  }

  .column-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 4px 8px 4px;
  }

  .column-title {
    font-size: 10px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
  }

  .column-count {
    font-size: 9px;
    color: var(--text-tertiary);
    background: transparent;
    padding: 0;
  }

  .column-tasks {
    flex: 1;
    padding: 0;
    overflow-y: auto;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 0;
    min-height: 60px;
  }

  .kanban-column.drag-over .column-tasks::after {
    content: '↓ Drop at end';
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 4px;
    padding: 12px 8px;
    border: 2px dashed var(--accent-primary);
    border-radius: 4px;
    background: rgba(var(--accent-rgb, 59, 130, 246), 0.08);
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--accent-primary);
  }

  /* Hide the bottom drop zone when hovering over a specific task */
  .kanban-column.drag-over .column-tasks:has(.drag-over-task)::after {
    display: none;
  }

  .task-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    border-radius: 4px;
    padding: 10px 12px;
    cursor: grab;
    transition: all 0.15s;
    position: relative;
    width: 100%;
    box-sizing: border-box;
  }

  .task-card:hover {
    border-color: var(--border-primary);
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }

  .task-card.dragging {
    opacity: 0.3;
    cursor: grabbing;
  }

  .task-card.drag-over-task {
    position: relative;
    margin-top: 40px;
    transition: margin-top 0.15s ease;
  }

  .task-card.drag-over-task::before {
    content: '';
    position: absolute;
    top: -36px;
    left: 0;
    right: 0;
    height: 32px;
    background: rgba(var(--accent-rgb, 59, 130, 246), 0.1);
    border-radius: 4px;
    border: 2px dashed var(--accent-primary);
  }

  .task-card.drag-over-task::after {
    content: '↓ Drop here';
    position: absolute;
    top: -32px;
    left: 0;
    right: 0;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--accent-primary);
  }

  .task-card:active {
    cursor: grabbing;
  }

  .task-title {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
    line-height: 1.4;
    padding-right: 28px;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }

  .task-description {
    font-size: 12px;
    color: var(--text-tertiary);
    line-height: 1.4;
    white-space: pre-wrap;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }

  .task-version-badge {
    display: inline-block;
    font-size: 9px;
    color: var(--accent-primary);
    background: rgba(255, 255, 255, 0.05);
    padding: 2px 6px;
    border-radius: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .task-actions {
    position: absolute;
    top: 6px;
    right: 4px;
    display: flex;
    gap: 1px;
    align-items: center;
    opacity: 0;
    transition: opacity 0.15s;
  }

  .task-card:hover .task-actions {
    opacity: 1;
  }

  .status-select, .version-select {
    flex: 1;
    padding: 4px 6px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    color: var(--text-primary);
    font-size: 9px;
    cursor: pointer;
  }

  .edit-btn, .delete-btn, .copy-btn {
    width: 18px;
    height: 18px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: 2px;
    color: var(--text-tertiary);
    font-size: 10px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .edit-btn:hover, .copy-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .delete-btn:hover {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
  }

  .empty-column {
    text-align: center;
    color: var(--text-tertiary);
    font-size: 10px;
    padding: 12px 8px;
    border: 1px dashed var(--border-secondary);
    border-radius: 3px;
    opacity: 0.6;
  }

  .kanban-column.drag-over .empty-column {
    border-color: var(--accent-primary);
    border-width: 2px;
    background: rgba(var(--accent-rgb, 59, 130, 246), 0.08);
    color: var(--accent-primary);
    opacity: 1;
  }

  /* Edit in place */
  .edit-title {
    width: 100%;
    padding: 6px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    color: var(--text-primary);
    font-size: 12px;
    margin-bottom: 6px;
  }

  .edit-description {
    width: 100%;
    padding: 6px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    color: var(--text-primary);
    font-size: 10px;
    resize: vertical;
    margin-bottom: 6px;
  }

  .edit-actions {
    display: flex;
    gap: 6px;
  }

  .save-btn, .cancel-btn {
    padding: 4px 10px;
    border-radius: 2px;
    font-size: 9px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .save-btn {
    background: var(--accent-primary);
    color: var(--bg-primary);
    border: none;
  }

  .save-btn:hover {
    opacity: 0.9;
  }

  .cancel-btn {
    background: var(--bg-secondary);
    color: var(--text-secondary);
    border: 1px solid var(--border-primary);
  }

  .cancel-btn:hover {
    background: var(--bg-hover);
  }

  /* List View */
  .list-view {
    overflow-x: auto;
  }

  .task-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
  }

  .task-table th,
  .task-table td {
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid var(--border-secondary);
  }

  .task-table th {
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-tertiary);
    background: var(--bg-secondary);
  }

  .task-table td {
    color: var(--text-primary);
  }

  .description-cell {
    color: var(--text-secondary);
    max-width: 250px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .empty-table {
    text-align: center;
    color: var(--text-tertiary);
    padding: 40px !important;
  }

  /* Modal */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1100;
  }

  .modal {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    width: 90%;
    max-width: 500px;
    box-shadow: var(--shadow-large);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-secondary);
  }

  .modal-header h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .modal-body {
    padding: 20px;
  }

  .input-field {
    width: 100%;
    padding: 10px 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    color: var(--text-primary);
    font-size: 13px;
    margin-bottom: 12px;
  }

  .input-field:focus,
  .textarea-field:focus,
  .select-field:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .textarea-field {
    width: 100%;
    padding: 10px 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    color: var(--text-primary);
    font-size: 13px;
    resize: vertical;
    margin-bottom: 12px;
  }

  .select-field {
    width: 100%;
    padding: 10px 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    color: var(--text-primary);
    font-size: 13px;
    cursor: pointer;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 16px 20px;
    border-top: 1px solid var(--border-secondary);
  }

  .action-btn {
    padding: 8px 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    color: var(--text-secondary);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .action-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .action-btn.primary {
    background: var(--accent-primary);
    color: var(--bg-primary);
    border: none;
  }

  .action-btn.primary:hover {
    opacity: 0.9;
  }

  .action-btn.danger {
    background: #ef4444;
    color: white;
    border: none;
  }

  .action-btn.danger:hover {
    background: #dc2626;
  }

  /* Versions Menu */
  .versions-menu-container {
    position: relative;
  }

  .versions-menu-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 0;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }

  .versions-menu-btn:hover {
    color: var(--text-primary);
  }

  .chevron {
    font-size: 8px;
    opacity: 0.7;
  }

  .versions-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    margin-top: 4px;
    min-width: 280px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    box-shadow: var(--shadow-large);
    z-index: 100;
    overflow: hidden;
  }

  .versions-list {
    max-height: 300px;
    overflow-y: auto;
  }

  .version-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    border-bottom: 1px solid var(--border-secondary);
    cursor: pointer;
    transition: background 0.2s;
  }

  .version-item:last-child {
    border-bottom: none;
  }

  .version-item:hover {
    background: var(--bg-hover);
  }

  .version-item.drag-over {
    background: var(--bg-hover);
    border-top: 2px solid var(--accent-primary);
  }

  .version-item.is-backlog {
    cursor: default;
    background: var(--bg-secondary);
  }

  .version-checkbox-item {
    cursor: pointer;
  }

  .version-checkbox-item input[type="checkbox"],
  .version-checkbox-label input[type="checkbox"] {
    appearance: none;
    -webkit-appearance: none;
    width: 16px;
    height: 16px;
    margin-right: 10px;
    border: 1.5px solid var(--border-primary);
    border-radius: 3px;
    background: var(--bg-secondary);
    cursor: pointer;
    position: relative;
    transition: all 0.15s ease;
    flex-shrink: 0;
  }

  .version-checkbox-item input[type="checkbox"]:hover,
  .version-checkbox-label input[type="checkbox"]:hover {
    border-color: var(--text-tertiary);
  }

  .version-checkbox-item input[type="checkbox"]:checked,
  .version-checkbox-label input[type="checkbox"]:checked {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
  }

  .version-checkbox-item input[type="checkbox"]:checked::after,
  .version-checkbox-label input[type="checkbox"]:checked::after {
    content: '';
    position: absolute;
    left: 4.5px;
    top: 1.5px;
    width: 4px;
    height: 8px;
    border: solid var(--bg-primary);
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
  }

  .version-checkbox-label {
    display: flex;
    align-items: center;
    flex: 1;
    cursor: pointer;
  }

  .version-name {
    flex: 1;
    font-size: 12px;
    color: var(--text-primary);
  }

  .version-task-count {
    font-size: 10px;
    color: var(--text-tertiary);
    padding: 2px 6px;
    background: var(--bg-secondary);
    border-radius: 10px;
  }

  .version-actions {
    display: flex;
    gap: 2px;
    opacity: 0;
    transition: opacity 0.2s;
  }

  .version-item:hover .version-actions {
    opacity: 1;
  }

  .version-action-btn {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-tertiary);
    border-radius: 2px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .version-action-btn:hover:not(:disabled) {
    background: var(--bg-secondary);
    border-color: var(--border-primary);
    color: var(--text-primary);
  }

  .version-action-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .version-action-btn.delete:hover:not(:disabled) {
    background: #ef4444;
    border-color: #ef4444;
    color: white;
  }

  .version-edit-input {
    flex: 1;
    padding: 4px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--accent-primary);
    border-radius: 2px;
    color: var(--text-primary);
    font-size: 12px;
  }

  .version-edit-input:focus {
    outline: none;
  }

  .versions-add-section {
    padding: 10px 12px;
    border-top: 1px solid var(--border-secondary);
    background: var(--bg-secondary);
  }

  .add-version-in-menu {
    width: 100%;
    padding: 8px 12px;
    background: transparent;
    border: 1px dashed var(--border-primary);
    color: var(--text-tertiary);
    border-radius: 2px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .add-version-in-menu:hover {
    border-color: var(--border-hover);
    color: var(--text-primary);
    background: var(--bg-hover);
  }

  .new-version-row {
    display: flex;
    gap: 6px;
    align-items: center;
  }

  .new-version-input-field {
    flex: 1;
    padding: 6px 8px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    color: var(--text-primary);
    font-size: 11px;
  }

  .new-version-input-field:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  /* Delete Version Modal */
  .delete-version-modal {
    max-width: 400px;
  }

  .delete-warning {
    margin: 0 0 16px 0;
    font-size: 13px;
    color: var(--text-primary);
  }

  .reassign-info {
    margin: 0 0 8px 0;
    font-size: 12px;
    color: var(--text-secondary);
  }

  .no-tasks-info {
    margin: 0;
    font-size: 12px;
    color: var(--text-tertiary);
  }

  /* Delete Task Modal */
  .delete-task-modal {
    max-width: 450px;
  }

  .delete-task-preview {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 4px;
    padding: 12px 16px;
  }

  .delete-task-title {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 6px;
  }

  .delete-task-description {
    font-size: 12px;
    color: var(--text-tertiary);
    line-height: 1.4;
    white-space: pre-wrap;
    max-height: 100px;
    overflow-y: auto;
  }

  .small-btn {
    padding: 4px 8px;
    background: var(--accent-primary);
    color: var(--bg-primary);
    border: none;
    border-radius: 2px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s;
  }

  .small-btn:hover {
    opacity: 0.9;
  }

  .small-btn.cancel {
    background: var(--bg-secondary);
    color: var(--text-secondary);
    border: 1px solid var(--border-primary);
  }

  .small-btn.cancel:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  /* Quick Add */
  .column-header-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .quick-add-btn {
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    border-radius: 2px;
    font-size: 14px;
    font-weight: 400;
    cursor: pointer;
    transition: all 0.15s;
    opacity: 0;
  }

  .column-header:hover .quick-add-btn {
    opacity: 1;
  }

  .quick-add-btn:hover {
    color: var(--accent-primary);
  }

  .quick-add-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    border-radius: 3px;
    padding: 6px;
  }

  .quick-add-input {
    width: 100%;
    padding: 6px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    color: var(--text-primary);
    font-size: 12px;
  }

  .quick-add-input:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .empty-column {
    cursor: pointer;
    transition: all 0.15s;
  }

  .empty-column:hover {
    border-color: var(--border-primary);
    color: var(--text-secondary);
    opacity: 1;
  }

  @media (max-width: 768px) {
    .kanban-board {
      grid-template-columns: 1fr;
    }
  }

  .spinner {
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spin 0.75s linear infinite;
    vertical-align: middle;
    margin-right: 4px;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Task Detail Modal */
  .task-detail-backdrop {
    backdrop-filter: blur(4px);
  }

  .task-detail-modal {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-large);
    overflow: hidden;
  }

  .task-detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-secondary);
    background: var(--bg-secondary);
  }

  .task-detail-meta {
    display: flex;
    gap: 10px;
    align-items: center;
  }

  .task-detail-status {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 4px 10px;
    border-radius: 3px;
  }

  .task-detail-status.status-todo {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
  }

  .task-detail-status.status-in_progress {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
  }

  .task-detail-status.status-done {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
  }

  .task-detail-version {
    font-size: 10px;
    color: var(--text-tertiary);
    padding: 4px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    border-radius: 3px;
  }

  .task-detail-body {
    flex: 1;
    padding: 24px;
    overflow-y: auto;
  }

  .task-detail-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 16px 0;
    line-height: 1.4;
  }

  .task-detail-description {
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.6;
    white-space: pre-wrap;
  }

  .task-detail-description .no-description {
    font-style: italic;
    color: var(--text-tertiary);
  }

  .task-detail-title-input {
    width: 100%;
    padding: 12px 14px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-primary);
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 16px;
  }

  .task-detail-title-input:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .task-detail-description-input {
    width: 100%;
    padding: 12px 14px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-primary);
    font-size: 14px;
    line-height: 1.5;
    resize: vertical;
    min-height: 120px;
    margin-bottom: 20px;
  }

  .task-detail-description-input:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .task-detail-fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .task-detail-field {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .task-detail-field label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
  }

  .task-detail-field select {
    padding: 10px 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-primary);
    font-size: 13px;
    cursor: pointer;
  }

  .task-detail-field select:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .task-detail-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-top: 1px solid var(--border-secondary);
    background: var(--bg-secondary);
  }

  .task-detail-footer .footer-left {
    display: flex;
    gap: 10px;
  }

  .task-detail-footer .footer-right {
    display: flex;
    gap: 10px;
  }
</style>
