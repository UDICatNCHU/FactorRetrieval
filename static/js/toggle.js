document.addEventListener('DOMContentLoaded', function() {
    // 獲取頁面元素
    const checkboxes = document.querySelectorAll('.toggle-checkbox');
    const selectAllBtn = document.getElementById('selectAll');
    const deselectAllBtn = document.getElementById('deselectAll');
    const selectedCountEl = document.getElementById('selectedCount');
    
    // 更新已選擇的數量
    function updateSelectedCount() {
        const selectedCount = document.querySelectorAll('.toggle-checkbox:checked').length;
        selectedCountEl.textContent = selectedCount;
    }
    
    // 為每個checkbox添加事件監聽
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            updateSelectedCount();
        });
    });
    
    // 全選按鈕
    selectAllBtn.addEventListener('click', () => {
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
        updateSelectedCount();
    });
    
    // 清除按鈕
    deselectAllBtn.addEventListener('click', () => {
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        updateSelectedCount();
    });
    
    // 初始化計數器
    updateSelectedCount();
});
