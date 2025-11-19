import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Tag, Space, Modal, Form, Input, Select, InputNumber, Checkbox, message, Spin, Row, Col, Divider, Descriptions } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UserOutlined, TeamOutlined, ThunderboltOutlined, EyeOutlined, ShareAltOutlined, EnvironmentOutlined } from '@ant-design/icons';

const { Option } = Select;

const Character: React.FC = () => {
  const [form] = Form.useForm();
  const [batchForm] = Form.useForm();
  const [modalVisible, setModalVisible] = useState(false);
  const [batchModalVisible, setBatchModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [characters, setCharacters] = useState<any[]>([]);
  const [worldViews, setWorldViews] = useState<any[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<any>(null);
  const [geographyOptions, setGeographyOptions] = useState<any>({ regions: [], locations: [] });
  // 固定的角色类型选项（简化版）
  const roleTypes = [
    { value: '主角', label: '主角', description: '故事中心角色' },
    { value: '配角', label: '配角', description: '配角' },
    { value: '正义伙伴', label: '正义伙伴', description: '支持主角的正面角色' },
    { value: '反派', label: '反派', description: '与主角对立的反面角色' },
    { value: '情人', label: '情人', description: '与主角有情感关系的角色' },
    { value: '其他', label: '其他', description: '其他类型角色' },
    { value: '特殊', label: '特殊', description: '特殊身份角色' }
  ];
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [batchDeleteLoading, setBatchDeleteLoading] = useState(false);
  
  // 关系管理相关状态
  const [relationships, setRelationships] = useState([]);
  const [selectedProtagonist, setSelectedProtagonist] = useState(null);
  
  // 全局关系生成相关状态
  const [globalRelationshipModalVisible, setGlobalRelationshipModalVisible] = useState(false);
  const [globalRelationshipLoading, setGlobalRelationshipLoading] = useState(false);
  const [globalRelationshipForm] = Form.useForm();
  const [globalRelationshipData, setGlobalRelationshipData] = useState<any>(null);
  
  // 监听批量生成表单的角色数量
  const characterCount = Form.useWatch('character_count', batchForm);

  // 监听编辑模态框的打开，设置表单值
  useEffect(() => {
    if (editModalVisible && selectedCharacter) {
      console.log('设置编辑表单值:', selectedCharacter);
      console.log('角色的worldview_id:', selectedCharacter.worldview_id);
      console.log('可用的世界观列表:', worldViews);
      console.log('匹配的世界观:', worldViews.find(w => w.worldview_id === selectedCharacter.worldview_id));
      
      // 检查worldview_id是否存在
      let worldviewId = selectedCharacter.worldview_id;
      if (!worldviewId) {
        console.warn('角色的worldview_id为空或未定义:', selectedCharacter);
        // 如果有可用的世界观，使用第一个作为默认值
        if (worldViews.length > 0) {
          worldviewId = worldViews[0].worldview_id;
          console.log('使用默认世界观:', worldViews[0]);
          message.info(`该角色没有关联的世界观，已自动选择: ${worldViews[0].name}`);
        } else {
          message.warning('该角色没有关联的世界观，且没有可用的世界观');
        }
      }
      
      form.setFieldsValue({
        worldview_id: worldviewId || undefined, // 如果为空则设置为undefined
        description: selectedCharacter.background || '',
        role_type: selectedCharacter.role_type,
        additional_requirements: ''
      });
      
      // 验证表单值是否设置成功
      setTimeout(() => {
        const formValues = form.getFieldsValue();
        console.log('表单实际值:', formValues);
      }, 100);
    }
  }, [editModalVisible, selectedCharacter, form, worldViews]);

  // 加载数据
  useEffect(() => {
    loadWorldViews();
    loadCharacters();
  }, []);

  const loadWorldViews = async () => {
    try {
      console.log('开始加载世界观...');
      const response = await fetch('http://localhost:8001/api/v1/world/simple-list');
      console.log('世界观API响应状态:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('世界观数据:', data);
      console.log('世界观数据结构:', data.worldviews);
      if (data.worldviews && data.worldviews.length > 0) {
        console.log('第一个世界观:', data.worldviews[0]);
        console.log('第一个世界观的ID:', data.worldviews[0].worldview_id);
      }
      setWorldViews(data.worldviews || []);
    } catch (error) {
      console.error('加载世界观失败:', error);
      message.error('加载世界观失败，请检查后端服务是否启动');
    }
  };

  const loadGeographyOptions = async (worldviewId: string) => {
    try {
      console.log('=== 开始加载地理位置选项 ===');
      console.log('世界观ID:', worldviewId);
      console.log('当前geographyOptions状态:', geographyOptions);
      
      const response = await fetch(`http://localhost:8001/api/v1/character/geography/${worldviewId}`);
      console.log('API响应状态:', response.status);
      
      if (!response.ok) {
        if (response.status === 404) {
          console.log('世界观没有地理设定');
          setGeographyOptions({ regions: [], locations: [] });
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('API返回数据:', data);
      console.log('区域数量:', data.regions?.length || 0);
      console.log('区域列表:', data.regions);
      
      setGeographyOptions(data);
      console.log('已设置地理位置选项，新状态:', data);
      
      // 验证状态是否更新
      setTimeout(() => {
        console.log('1秒后验证状态:', geographyOptions);
      }, 1000);
      
    } catch (error) {
      console.error('加载地理位置选项失败:', error);
      setGeographyOptions({ regions: [], locations: [] });
    }
  };

  const loadCharacters = async () => {
    try {
      console.log('开始加载角色...');
      const response = await fetch('http://localhost:8001/api/v1/character/list');
      console.log('角色API响应状态:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('角色数据:', data);
      // 调试：检查第一个角色的worldview_id
      if (data && data.length > 0) {
        console.log('第一个角色的worldview_id:', data[0].worldview_id);
        console.log('第一个角色完整数据:', data[0]);
      }
      setCharacters(data || []);
    } catch (error) {
      console.error('加载角色失败:', error);
      message.error('加载角色失败，请检查后端服务是否启动');
    }
  };


  const columns = [
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <UserOutlined />
          {text}
        </Space>
      ),
    },
    {
      title: '角色类型',
      dataIndex: 'role_type',
      key: 'role_type',
      render: (type: string) => {
        const colorMap: { [key: string]: string } = {
          '主角': 'red',
          '配角': 'green',
          '正义伙伴': 'blue',
          '反派': 'purple',
          '情人': 'pink',
          '其他': 'orange',
          '特殊': 'cyan'
        };
        return <Tag color={colorMap[type] || 'default'}>{type}</Tag>;
      },
    },
    {
      title: '基本信息',
      key: 'basic_info',
      render: (_, record) => (
        <div>
          <div><strong>年龄：</strong>{record.age}岁</div>
          <div><strong>性别：</strong>{record.gender}</div>
          {record.appearance && (
            <div><strong>外貌：</strong>{record.appearance}</div>
          )}
        </div>
      ),
    },
    {
      title: '性格',
      dataIndex: 'personality_traits',
      key: 'personality_traits',
      render: (traits: any) => {
        // 处理不同的数据格式
        let displayText = '';
        
        if (typeof traits === 'string') {
          // 新格式：字符串
          displayText = traits;
        } else if (Array.isArray(traits)) {
          // 旧格式：对象数组
          displayText = traits.map(trait => {
            if (typeof trait === 'string') {
              return trait;
            } else if (trait && typeof trait === 'object') {
              return trait.trait || trait.name || JSON.stringify(trait);
            }
            return '';
          }).filter(Boolean).join('、');
        } else if (traits && typeof traits === 'object') {
          // 单个对象
          displayText = traits.trait || traits.name || JSON.stringify(traits);
        }
        
        return (
          <div style={{ 
            maxWidth: '200px', 
            overflow: 'hidden', 
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {displayText || '暂无性格特质'}
          </div>
        );
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button type="link" icon={<EyeOutlined />} onClick={() => handleViewCharacter(record)}>查看</Button>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEditCharacter(record)}>编辑</Button>
          <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDeleteCharacter(record)}>删除</Button>
        </Space>
      ),
    },
  ];

  const handleCreateCharacter = async (values: any) => {
    setLoading(true);
    try {
      // 构建地理位置信息
      let locationInfo = '';
      if (values.current_region && values.current_location) {
        locationInfo = `${values.current_region} - ${values.current_location}`;
      } else if (values.current_region) {
        locationInfo = values.current_region;
      } else if (values.current_location) {
        locationInfo = values.current_location;
      }

      const requestData = {
        worldview_id: values.worldview_id,
        description: values.description,
        role_type: values.role_type,
        additional_requirements: values.additional_requirements || ""
      };

      // 如果选择了地理位置，添加到描述中
      if (locationInfo) {
        requestData.additional_requirements = (requestData.additional_requirements || '') + 
          (requestData.additional_requirements ? '；' : '') + 
          `地理位置：${locationInfo}`;
      }

      console.log('发送角色创建请求数据:', requestData);

      const response = await fetch('http://localhost:8001/api/v1/character/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
        signal: AbortSignal.timeout(600000), // 600秒超时
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '生成失败');
      }

      const character = await response.json();
      console.log('角色生成结果:', character);
      
      message.success('角色生成成功！');
      setModalVisible(false);
      form.resetFields();
      // 重新加载角色列表
      await loadCharacters();
    } catch (error: any) {
      console.error('创建角色失败:', error);
      let errorMessage = '创建角色失败';
      
      if (error.message) {
        errorMessage += ': ' + error.message;
      } else if (typeof error === 'string') {
        errorMessage += ': ' + error;
      } else if (error.detail) {
        errorMessage += ': ' + error.detail;
      } else {
        errorMessage += ': 未知错误';
      }
      
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchCreateCharacters = async (values: any) => {
    setBatchLoading(true);
    try {
      // 构建地理位置信息
      let locationInfo = '';
      if (values.current_region && values.current_location) {
        locationInfo = `${values.current_region} - ${values.current_location}`;
      } else if (values.current_region) {
        locationInfo = values.current_region;
      } else if (values.current_location) {
        locationInfo = values.current_location;
      }

      const requestData = {
        worldview_id: values.worldview_id,
        description: values.description,
        character_count: values.character_count,
        role_types: values.role_types,
        additional_requirements: values.additional_requirements || ""
      };

      // 如果选择了地理位置，添加到描述中
      if (locationInfo) {
        requestData.additional_requirements = (requestData.additional_requirements || '') + 
          (requestData.additional_requirements ? '；' : '') + 
          `地理位置：${locationInfo}`;
      }

      console.log('发送批量角色创建请求数据:', requestData);

      const response = await fetch('http://localhost:8001/api/v1/character/batch-create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
        signal: AbortSignal.timeout(600000), // 600秒超时
      });

      if (!response.ok) {
        throw new Error('批量生成失败');
      }

      const data = await response.json();
      if (data.success) {
        message.success(`成功生成${data.total_count}个角色！`);
        setBatchModalVisible(false);
        batchForm.resetFields();
        // 重新加载角色列表
        await loadCharacters();
      } else {
        message.error(data.message || '批量生成失败');
      }
    } catch (error: any) {
      console.error('批量创建角色失败:', error);
      let errorMessage = '批量创建角色失败';
      
      if (error.message) {
        errorMessage += ': ' + error.message;
      } else if (typeof error === 'string') {
        errorMessage += ': ' + error;
      } else if (error.detail) {
        errorMessage += ': ' + error.detail;
      } else {
        errorMessage += ': 未知错误';
      }
      
      message.error(errorMessage);
    } finally {
      setBatchLoading(false);
    }
  };

  // 查看角色详情
  const handleViewCharacter = (character: any) => {
    setSelectedCharacter(character);
    setViewModalVisible(true);
  };

  // 编辑角色
  const handleEditCharacter = (character: any) => {
    console.log('编辑角色数据:', character);
    console.log('角色的worldview_id:', character.worldview_id);
    setSelectedCharacter(character);
    
    // 处理JSON字段的格式化
    const formatJsonField = (field: any) => {
      if (!field) return '';
      if (typeof field === 'string') return field;
      // 如果是数组，直接转换为JSON字符串
      if (Array.isArray(field)) return JSON.stringify(field, null, 2);
      return JSON.stringify(field, null, 2);
    };

    // 预填充表单数据
    const formData = {
      // 基本信息
      name: character.name,
      age: character.age,
      gender: character.gender,
      role_type: character.role_type,
      worldview_id: character.worldview_id,
      
      // 修炼信息
      cultivation_level: character.cultivation_level,
      element_type: character.element_type,
      current_location: character.current_location,
      organization_id: character.organization_id,
      
      // 地理位置字段解析
      current_region: '',
      current_location: character.current_location || '',
      
      // 外貌和背景
      background: character.background,
      appearance: character.appearance || '',
      
      // JSON字段
      personality_traits: character.personality_traits || '',
      main_goals: character.main_goals || '',
      short_term_goals: character.short_term_goals || '',
      techniques: formatJsonField(character.techniques),
      weaknesses: character.weaknesses || '',
      
      // 特殊字段
      values: character.values || '',
      turning_point: character.turning_point || '',
      
      // 新增字段
      relationship_text: character.relationship_text || '',
      status: character.status || 'active',
      created_at: character.created_at ? new Date(character.created_at).toLocaleString() : ''
    };

    // 解析地理位置信息
    if (character.current_location) {
      const locationParts = character.current_location.split(' - ');
      if (locationParts.length === 2) {
        formData.current_region = locationParts[0];
        formData.current_location = locationParts[1];
      }
    }

    // 加载地理位置选项
    if (character.worldview_id) {
      loadGeographyOptions(character.worldview_id);
    }

    console.log('表单填充数据:', formData);
    
    // 先重置表单，再设置值
    form.resetFields();
    form.setFieldsValue(formData);
    
    setEditModalVisible(true);
  };

  // 删除角色
  const handleDeleteCharacter = (character: any) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除角色"${character.name}"吗？此操作不可撤销。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          setLoading(true);
          const response = await fetch(`http://localhost:8001/api/v1/character/${character.id}`, {
            method: 'DELETE',
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '删除失败');
          }

          const result = await response.json();
          message.success(result.message || '角色删除成功！');
          await loadCharacters(); // 重新加载角色列表
        } catch (error: any) {
          console.error('删除角色失败:', error);
          message.error('删除角色失败: ' + error.message);
        } finally {
          setLoading(false);
        }
      },
    });
  };

  const handleBatchDeleteCharacters = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的角色');
      return;
    }

    Modal.confirm({
      title: '确认批量删除',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个角色吗？此操作不可撤销。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          setBatchDeleteLoading(true);
          const response = await fetch('http://localhost:8001/api/v1/character/batch', {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              character_ids: selectedRowKeys
            }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '批量删除失败');
          }

          const result = await response.json();
          message.success(result.message || '批量删除成功！');
          setSelectedRowKeys([]); // 清空选择
          await loadCharacters(); // 重新加载角色列表
        } catch (error: any) {
          console.error('批量删除角色失败:', error);
          message.error('批量删除角色失败: ' + error.message);
        } finally {
          setBatchDeleteLoading(false);
        }
      },
    });
  };



  // 打开全局关系生成模态框
  const openGlobalRelationshipModal = () => {
    setGlobalRelationshipModalVisible(true);
    globalRelationshipForm.setFieldsValue({
      worldview_id: worldViews.length > 0 ? worldViews[0].worldview_id : '',
      relationship_requirements: '',
      generate_perspectives: true
    });
  };

  // 全局关系生成功能
  const handleGenerateGlobalRelationships = async (values: any) => {
    console.log('全局关系生成表单数据:', values);
    setGlobalRelationshipLoading(true);
    try {
      const requestData = {
        worldview_id: values.worldview_id,
        relationship_requirements: values.relationship_requirements || "",
        generate_perspectives: values.generate_perspectives !== false
      };
      console.log('发送全局关系生成请求数据:', requestData);
      
      const response = await fetch('http://localhost:8001/api/v1/character/relationships/global', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '全局关系生成失败');
      }

      const result = await response.json();
      console.log('全局关系生成结果:', result);
      
      // 保存全局关系数据
      setGlobalRelationshipData(result);
      
      // 将个人关系视角保存到每个角色的metadata中
      if (result.perspectives) {
        for (const [characterId, perspective] of Object.entries(result.perspectives)) {
          // 更新角色列表中的对应角色
          setCharacters(prevCharacters => 
            prevCharacters.map(char => 
              char.id === characterId 
                ? {
                    ...char,
                    metadata: {
                      ...char.metadata,
                      relationship_text: perspective
                    }
                  }
                : char
            )
          );
        }
      }
      
      message.success('全局关系网络生成成功！个人关系视角已自动分配到各角色');
      setGlobalRelationshipModalVisible(false);
      globalRelationshipForm.resetFields();
      
    } catch (error: any) {
      console.error('全局关系生成失败:', error);
      message.error(`全局关系生成失败: ${error.message}`);
    } finally {
      setGlobalRelationshipLoading(false);
    }
  };

  // 更新角色
  const handleUpdateCharacter = async (values: any) => {
    if (!selectedCharacter) return;
    
    setLoading(true);
    try {
      // 处理JSON字段
      const parseJsonField = (field: string) => {
        if (!values[field] || values[field].trim() === '') return null;
        try {
          return JSON.parse(values[field]);
        } catch (e) {
          console.warn(`解析${field}字段失败:`, e);
          return null;
        }
      };

      // 构建更新数据
      const updateData = {
        // 基本信息
        name: values.name,
        age: values.age,
        gender: values.gender,
        role_type: values.role_type,
        worldview_id: values.worldview_id,
        
        // 修炼信息
        cultivation_level: values.cultivation_level,
        element_type: values.element_type,
        current_location: values.current_location,
        organization_id: values.organization_id,
        
        // 外貌和背景
        background: values.background,
        
        // 文本字段
        personality_traits: values.personality_traits || '',
        main_goals: values.main_goals || '',
        short_term_goals: values.short_term_goals || '',
        weaknesses: values.weaknesses || '',
        appearance: values.appearance || '',
        turning_point: values.turning_point || '',
        relationship_text: values.relationship_text || '',
        
        // JSON字段
        techniques: parseJsonField('techniques'),
        metadata: {},
        
        // 状态字段
        status: values.status || 'active'
      };

      // 处理地理位置字段
      let locationInfo = '';
      if (values.current_region && values.current_location) {
        locationInfo = `${values.current_region} - ${values.current_location}`;
      } else if (values.current_region) {
        locationInfo = values.current_region;
      } else if (values.current_location) {
        locationInfo = values.current_location;
      }
      updateData.current_location = locationInfo;

      // 处理价值观字段（独立字段）
      if (values.values) {
        updateData.values = values.values;
      }

      console.log('发送更新数据:', updateData);

      const response = await fetch(`http://localhost:8001/api/v1/character/${selectedCharacter.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '更新失败');
      }

      message.success('角色更新成功！');
      setEditModalVisible(false);
      form.resetFields();
      await loadCharacters(); // 重新加载角色列表
    } catch (error: any) {
      console.error('更新角色失败:', error);
      let errorMessage = '更新角色失败';
      
      if (error.message) {
        errorMessage += ': ' + error.message;
      } else if (typeof error === 'string') {
        errorMessage += ': ' + error;
      } else if (error.detail) {
        errorMessage += ': ' + error.detail;
      } else if (error.response?.data?.detail) {
        errorMessage += ': ' + error.response.data.detail;
      } else {
        errorMessage += ': 未知错误';
      }
      
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card 
        title="角色管理" 
        extra={
          <Space>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setModalVisible(true)}
              loading={loading}
            >
              单个角色
            </Button>
            <Button 
              type="default" 
              icon={<TeamOutlined />}
              onClick={() => setBatchModalVisible(true)}
              loading={batchLoading}
            >
              批量生成
            </Button>
            <Button 
              type="default" 
              icon={<ShareAltOutlined />}
              onClick={openGlobalRelationshipModal}
              loading={globalRelationshipLoading}
            >
              生成关系网络
            </Button>
            <Button 
              danger
              icon={<DeleteOutlined />}
              onClick={handleBatchDeleteCharacters}
              loading={batchDeleteLoading}
              disabled={selectedRowKeys.length === 0}
            >
              批量删除 ({selectedRowKeys.length})
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={characters}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          rowSelection={{
            selectedRowKeys,
            onChange: setSelectedRowKeys,
            getCheckboxProps: (record) => ({
              name: record.name,
            }),
          }}
        />
      </Card>

      <Modal
        title="创建单个角色"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={800}
        confirmLoading={loading}
      >
        <Form form={form} onFinish={handleCreateCharacter} layout="vertical">
          <Form.Item
            name="worldview_id"
            label="选择世界观"
            rules={[{ required: true, message: '请选择世界观' }]}
          >
            <Select 
              placeholder="请选择世界观" 
              loading={worldViews.length === 0}
              onChange={(value) => {
                console.log('世界观选择变化，ID:', value);
                loadGeographyOptions(value);
                form.setFieldsValue({ current_region: '', current_location: '' }); // 清空地理位置
              }}
            >
              {worldViews.map((world: any) => (
                <Option key={world.worldview_id} value={world.worldview_id}>
                  {world.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="current_region"
                label="所在区域"
                extra="选择角色所在的大区域"
              >
                <Select 
                  placeholder={geographyOptions.regions.length === 0 ? "请先选择世界观" : "请选择区域"} 
                  allowClear
                  disabled={false}
                >
                  {console.log('当前geographyOptions:', geographyOptions)}
                  {console.log('regions数量:', geographyOptions.regions?.length || 0)}
                  {geographyOptions.regions && geographyOptions.regions.length > 0 ? (
                    geographyOptions.regions.map((region: any, index: number) => (
                      <Option key={`region-${index}`} value={region.name}>
                        {region.name}
                      </Option>
                    ))
                  ) : (
                    <Option disabled value="">暂无区域数据</Option>
                  )}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="current_location"
                label="具体位置"
                extra="填写具体的城市、门派、村庄等"
              >
                <Input 
                  placeholder="如：天剑宗、青云城、无名村等"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="角色描述"
            rules={[{ required: true, message: '请输入角色描述' }]}
          >
            <Input.TextArea 
              rows={5} 
              placeholder="请用一句话描述你想要创建的角色，例如：一个年轻的修仙者，性格勇敢但有些冲动，来自小门派，梦想成为仙尊"
            />
          </Form.Item>

          <Form.Item
            name="role_type"
            label="角色类型"
            rules={[{ required: true, message: '请选择角色类型' }]}
          >
            <Select placeholder="请选择角色类型">
              {roleTypes.map((roleType: any) => (
                <Option key={roleType.value} value={roleType.value}>
                  {roleType.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="additional_requirements"
            label="额外要求（可选）"
          >
            <Input.TextArea 
              rows={2} 
              placeholder="可以添加额外的要求，例如：年龄范围、性别、特殊能力、外貌特征等"
            />
          </Form.Item>

          <Divider />
          
          <div style={{ textAlign: 'center', color: '#666' }}>
            <UserOutlined style={{ marginRight: 8 }} />
            系统将根据您的描述智能生成符合世界观的角色
          </div>
        </Form>
      </Modal>

      {/* 批量生成角色模态框 */}
      <Modal
        title="批量生成角色"
        open={batchModalVisible}
        onCancel={() => setBatchModalVisible(false)}
        onOk={() => batchForm.submit()}
        width={800}
        confirmLoading={batchLoading}
      >
        <Form form={batchForm} onFinish={handleBatchCreateCharacters} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="worldview_id"
                label="选择世界观"
                rules={[{ required: true, message: '请选择世界观' }]}
              >
                <Select 
                  placeholder="请选择世界观" 
                  loading={worldViews.length === 0}
                  onChange={(value) => {
                    console.log('批量创建-世界观选择变化，ID:', value);
                    loadGeographyOptions(value);
                    batchForm.setFieldsValue({ current_region: '', current_location: '' }); // 清空地理位置
                  }}
                >
                  {worldViews.map((world: any) => (
                    <Option key={world.worldview_id} value={world.worldview_id}>
                      {world.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="character_count"
                label="角色数量"
                rules={[{ required: true, message: '请输入角色数量' }]}
              >
                <InputNumber 
                  min={1} 
                  max={20} 
                  placeholder="1-20个角色" 
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="current_region"
                label="所在区域"
                extra="选择角色所在的大区域"
              >
                <Select 
                  placeholder={geographyOptions.regions.length === 0 ? "请先选择世界观" : "请选择区域"} 
                  allowClear
                  disabled={false}
                >
                  {console.log('当前geographyOptions:', geographyOptions)}
                  {console.log('regions数量:', geographyOptions.regions?.length || 0)}
                  {geographyOptions.regions && geographyOptions.regions.length > 0 ? (
                    geographyOptions.regions.map((region: any, index: number) => (
                      <Option key={`region-${index}`} value={region.name}>
                        {region.name}
                      </Option>
                    ))
                  ) : (
                    <Option disabled value="">暂无区域数据</Option>
                  )}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="current_location"
                label="具体位置"
                extra="填写具体的城市、门派、村庄等"
              >
                <Input 
                  placeholder="如：天剑宗、青云城、无名村等"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="角色描述"
            rules={[{ required: true, message: '请输入角色描述' }]}
          >
            <Input.TextArea 
              rows={5} 
              placeholder="请用一句话描述你想要生成的角色，例如：一群年轻的修仙者，他们来自不同的门派，有着不同的性格和背景"
            />
          </Form.Item>

          <Form.Item
            name="role_types"
            label="角色类型"
            rules={[{ required: true, message: '请选择至少一种角色类型' }]}
          >
            <Checkbox.Group>
              <Row>
                {roleTypes.map((roleType: any) => (
                  <Col span={8} key={roleType.value}>
                    <Checkbox value={roleType.value}>{roleType.label}</Checkbox>
                  </Col>
                ))}
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="additional_requirements"
            label="额外要求（可选）"
          >
            <Input.TextArea 
              rows={2} 
              placeholder="可以添加额外的要求，例如：年龄范围、性别比例、特殊能力等"
            />
          </Form.Item>

          <Divider />
          
          <div style={{ textAlign: 'center', color: '#666' }}>
            <ThunderboltOutlined style={{ marginRight: 8 }} />
            系统将根据您的描述和设置，智能生成{characterCount || '多个'}符合世界观的角色
          </div>
        </Form>
      </Modal>

      {/* 查看角色详情模态框 */}
      <Modal
        title="角色详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>
        ]}
        width="90%"
        style={{ maxWidth: 1200 }}
        bodyStyle={{ maxHeight: '80vh', overflowY: 'auto' }}
        className="character-detail-modal"
      >
        {selectedCharacter && (
          <Descriptions 
            bordered 
            column={{ xs: 1, sm: 1, md: 2, lg: 2, xl: 2, xxl: 2 }}
            size="middle"
            labelStyle={{ 
              fontWeight: 'bold', 
              backgroundColor: '#fafafa',
              minWidth: '120px'
            }}
            contentStyle={{ 
              wordBreak: 'break-word',
              maxWidth: '400px'
            }}
          >
            <Descriptions.Item label="姓名" span={2}>
              <Space>
                <UserOutlined />
                <strong style={{ fontSize: '16px' }}>{selectedCharacter.name}</strong>
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="角色类型">
              <Tag color={
                selectedCharacter.role_type === '主角' ? 'red' :
                selectedCharacter.role_type === '配角' ? 'green' :
                selectedCharacter.role_type === '正义伙伴' ? 'blue' :
                selectedCharacter.role_type === '反派' ? 'purple' :
                selectedCharacter.role_type === '情人' ? 'pink' :
                selectedCharacter.role_type === '其他' ? 'orange' :
                selectedCharacter.role_type === '特殊' ? 'cyan' : 'default'
              }>
                {selectedCharacter.role_type}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="年龄">
              {selectedCharacter.age}岁
            </Descriptions.Item>
            <Descriptions.Item label="性别">
              {selectedCharacter.gender}
            </Descriptions.Item>
            <Descriptions.Item label="外貌">
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '100px', 
                overflowY: 'auto',
                padding: '4px 0'
              }}>
                {selectedCharacter.appearance || '暂无外貌描述'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="背景" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '120px', 
                overflowY: 'auto',
                padding: '4px 0',
                lineHeight: '1.6'
              }}>
                {selectedCharacter.background || '暂无背景信息'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="性格特质" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '100px', 
                overflowY: 'auto',
                padding: '4px 0',
                lineHeight: '1.6'
              }}>
                {selectedCharacter.personality_traits || '暂无性格特质描述'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="价值观" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '80px', 
                overflowY: 'auto',
                padding: '4px 0'
              }}>
                {selectedCharacter.values || '暂无价值观信息'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="主要目标" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '100px', 
                overflowY: 'auto',
                padding: '4px 0',
                lineHeight: '1.6'
              }}>
                {selectedCharacter.main_goals || '暂无主要目标描述'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="短期目标" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '100px', 
                overflowY: 'auto',
                padding: '4px 0',
                lineHeight: '1.6'
              }}>
                {selectedCharacter.short_term_goals || '暂无短期目标描述'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="修炼境界">
              <Tag color="purple">{selectedCharacter.cultivation_level || '未知'}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="灵根属性">
              <Tag color="orange">{selectedCharacter.element_type || '未知'}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="地理位置" span={2}>
              <Space>
                <EnvironmentOutlined />
                <span>{selectedCharacter.current_location || '未知位置'}</span>
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="所属组织">
              <Tag color="blue">{selectedCharacter.organization_id || '无'}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="技能" span={2}>
              <Space wrap>
                {selectedCharacter.techniques && selectedCharacter.techniques.length > 0 ? (
                  selectedCharacter.techniques.map((tech: any, index: number) => (
                    <Tag key={index} color="orange">
                      {typeof tech === 'string' ? tech : `${tech.name} (${tech.level})`}
                    </Tag>
                  ))
                ) : (
                  <span style={{ color: '#999' }}>暂无技能</span>
                )}
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="弱点" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '100px', 
                overflowY: 'auto',
                padding: '4px 0',
                lineHeight: '1.6'
              }}>
                {selectedCharacter.weaknesses || '暂无弱点描述'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="转折点" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '80px', 
                overflowY: 'auto',
                padding: '4px 0'
              }}>
                {selectedCharacter.turning_point || '暂无转折点信息'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="个人关系视角" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '200px', 
                overflowY: 'auto',
                padding: '4px 0'
              }}>
                {(() => {
                  console.log('角色数据:', selectedCharacter);
                  console.log('关系文本:', selectedCharacter?.relationship_text);
                  return selectedCharacter?.relationship_text;
                })() ? (
                  <div style={{ 
                    lineHeight: '1.8', 
                    color: '#333',
                    fontSize: '14px',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {selectedCharacter.relationship_text}
                  </div>
                ) : (
                  <div>
                    <span style={{ color: '#999' }}>暂无个人关系视角信息</span>
                    <div style={{ marginTop: 8, fontSize: '12px', color: '#666' }}>
                      请先生成全局关系网络，系统将自动为每个角色分配个人关系视角
                    </div>
                  </div>
                )}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {new Date(selectedCharacter.created_at).toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={selectedCharacter.status === 'active' ? 'green' : 'red'}>
                {selectedCharacter.status === 'active' ? '活跃' : '非活跃'}
              </Tag>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      {/* 编辑角色模态框 */}
      <Modal
        title="编辑角色详情"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        onOk={() => form.submit()}
        width={1000}
        confirmLoading={loading}
      >
        <Form form={form} onFinish={handleUpdateCharacter} layout="vertical">
          {/* 基本信息卡片 */}
          <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="name"
                  label="角色姓名"
                  rules={[{ required: true, message: '请输入角色姓名' }]}
                >
                  <Input placeholder="请输入角色姓名" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="age"
                  label="年龄"
                  rules={[{ required: true, message: '请输入年龄' }]}
                >
                  <InputNumber min={0} max={1000} placeholder="请输入年龄" style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="gender"
                  label="性别"
                  rules={[{ required: true, message: '请选择性别' }]}
                >
                  <Select placeholder="请选择性别">
                    <Option value="男">男</Option>
                    <Option value="女">女</Option>
                    <Option value="其他">其他</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="role_type"
                  label="角色类型"
                  rules={[{ required: true, message: '请选择角色类型' }]}
                >
                  <Select placeholder="请选择角色类型">
                    {roleTypes.map(role => (
                      <Option key={role.value} value={role.value}>
                        {role.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="worldview_id"
                  label="世界观"
                  rules={[{ required: true, message: '请选择世界观' }]}
                >
                  <Select 
                    placeholder="请选择世界观"
                    onChange={(value) => {
                      console.log('编辑页面-世界观选择变化，ID:', value);
                      loadGeographyOptions(value);
                      form.setFieldsValue({ current_region: '', current_location: '' }); // 清空地理位置
                    }}
                  >
                    {worldViews.map((world: any) => (
                      <Option key={world.worldview_id} value={world.worldview_id}>
                        {world.name}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </Card>

          {/* 修炼信息卡片 */}
          <Card title="修炼信息" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="cultivation_level"
                  label="修炼境界"
                >
                  <Input placeholder="如：炼气境、筑基境、金丹境等" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="element_type"
                  label="灵根属性"
                >
                  <Input placeholder="如：火、水、木、金、土等" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="current_region"
                  label="所在区域"
                  extra="选择角色所在的大区域"
                >
                  <Select 
                    placeholder={geographyOptions.regions.length === 0 ? "请先选择世界观" : "请选择区域"} 
                    allowClear
                    disabled={false}
                  >
                    {geographyOptions.regions && geographyOptions.regions.length > 0 ? (
                      geographyOptions.regions.map((region: any, index: number) => (
                        <Option key={`region-${index}`} value={region.name}>
                          {region.name}
                        </Option>
                      ))
                    ) : (
                      <Option disabled value="">暂无区域数据</Option>
                    )}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="current_location"
                  label="具体位置"
                  extra="填写具体的城市、门派、村庄等"
                >
                  <Input 
                    placeholder="如：天剑宗、青云城、无名村等"
                  />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="organization_id"
                  label="所属组织"
                >
                  <Input placeholder="如：天剑宗、散修等" />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          {/* 外貌和背景卡片 */}
          <Card title="外貌和背景" size="small" style={{ marginBottom: 16 }}>
            <Form.Item
              name="appearance"
              label="外貌描述"
            >
              <Input.TextArea 
                rows={3} 
                placeholder="描述角色的外貌特征，如：身形精瘦，皮肤微黑，眼神灵动带笑，左肩有虎爪旧疤"
              />
            </Form.Item>

            <Form.Item
              name="background"
              label="背景故事"
              rules={[{ required: true, message: '请输入背景故事' }]}
            >
              <Input.TextArea 
                rows={6} 
                placeholder="详细描述角色的出身、经历、师门、地位等背景信息"
              />
            </Form.Item>
          </Card>

          {/* 性格特质卡片 */}
          <Card title="性格特质" size="small" style={{ marginBottom: 16 }}>
            <Form.Item
              name="personality_traits"
              label="性格特质"
            >
              <Input.TextArea 
                rows={4} 
                placeholder="描述角色的性格特质，如：勇敢无畏，正义感强，但有时过于冲动"
              />
            </Form.Item>
          </Card>

          {/* 目标和价值观卡片 */}
          <Card title="目标和价值观" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="main_goals"
                  label="主要目标"
                >
                  <Input.TextArea 
                    rows={6} 
                    placeholder="描述角色的主要目标，如：成为绝世强者，保护重要的人"
                  />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="short_term_goals"
                  label="短期目标"
                >
                  <Input.TextArea 
                    rows={6} 
                    placeholder="描述角色的短期目标，如：突破到金丹境，学会新的剑法"
                  />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="values"
                  label="价值观描述"
                >
                  <Input.TextArea 
                    rows={6} 
                    placeholder="描述角色的价值观和信念，如：虽身处乱世，仍坚信人命不该如草芥"
                  />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          {/* 技能和弱点卡片 */}
          <Card title="技能和弱点" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="techniques"
                  label="掌握的技能"
                  extra='JSON格式，如：[{"name": "基础拳法", "level": "初级"}]'
                >
                  <Input.TextArea 
                    rows={6} 
                    placeholder="输入JSON格式的技能数组"
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="weaknesses"
                  label="弱点和限制"
                >
                  <Input.TextArea 
                    rows={6} 
                    placeholder="描述角色的弱点和限制，如：缺乏实战经验，容易冲动"
                  />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          {/* 转折点和关系视角卡片 */}
          <Card title="转折点和关系视角" size="small" style={{ marginBottom: 16 }}>
            <Form.Item
              name="turning_point"
              label="重要转折点"
            >
              <Input.TextArea 
                rows={4} 
                placeholder="描述角色的重要转折点或关键事件"
              />
            </Form.Item>

            <Form.Item
              name="relationship_text"
              label="个人关系视角"
              extra="描述角色对其他角色的看法和关系"
            >
              <Input.TextArea 
                rows={6} 
                placeholder="描述角色对其他角色的看法、关系、态度等，如：对师父的敬重、对同门的友谊、对敌人的仇恨等"
              />
            </Form.Item>
          </Card>

          {/* 状态信息卡片 */}
          <Card title="状态信息" size="small">
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="status"
                  label="角色状态"
                >
                  <Select placeholder="请选择角色状态">
                    <Option value="active">活跃</Option>
                    <Option value="inactive">非活跃</Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="created_at"
                  label="创建时间"
                >
                  <Input disabled placeholder="系统自动生成" />
                </Form.Item>
              </Col>
            </Row>
          </Card>
        </Form>
      </Modal>


      {/* 全局关系生成模态框 */}
      <Modal
        title="生成全局关系网络"
        open={globalRelationshipModalVisible}
        onCancel={() => setGlobalRelationshipModalVisible(false)}
        onOk={() => globalRelationshipForm.submit()}
        width={800}
        confirmLoading={globalRelationshipLoading}
        okText="生成关系网络"
        cancelText="取消"
      >
        <Form form={globalRelationshipForm} onFinish={handleGenerateGlobalRelationships} layout="vertical">
          <Form.Item
            name="worldview_id"
            label="选择世界观"
            rules={[{ required: true, message: '请选择世界观' }]}
          >
            <Select placeholder="请选择世界观" loading={worldViews.length === 0}>
              {worldViews.map((world: any) => (
                <Option key={world.worldview_id} value={world.worldview_id}>
                  {world.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="relationship_requirements"
            label="关系生成要求（可选）"
            rules={[]}
          >
            <Input.TextArea 
              rows={4} 
              placeholder="可选：描述关系网络的具体要求，例如：主角为中心，包含正邪对立、师门情谊、爱情纠葛等。留空则自动生成"
            />
          </Form.Item>

          <Form.Item
            name="generate_perspectives"
            valuePropName="checked"
            initialValue={true}
          >
            <Checkbox>生成个人关系视角</Checkbox>
          </Form.Item>

          <div style={{ textAlign: 'center', color: '#666', marginTop: 16 }}>
            <ShareAltOutlined style={{ marginRight: 8 }} />
            系统将基于所有角色生成完整的关系网络，然后为每个角色分配个人视角
          </div>
        </Form>
      </Modal>

      {/* 全局关系网络展示模态框 */}
      {globalRelationshipData && (
        <Modal
          title="全局关系网络"
          open={!!globalRelationshipData}
          onCancel={() => setGlobalRelationshipData(null)}
          width={1200}
          footer={[
            <Button key="close" onClick={() => setGlobalRelationshipData(null)}>
              关闭
            </Button>
          ]}
        >
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <h3>关系网络概览</h3>
            <p>{globalRelationshipData.global_network?.network_description || '暂无描述'}</p>
            
            <h3>关系统计</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginBottom: '16px' }}>
              <div>
                <strong>总角色数：</strong>{globalRelationshipData.total_characters}
              </div>
              <div>
                <strong>总关系数：</strong>{globalRelationshipData.relationship_stats?.total_relationships || 0}
              </div>
              <div>
                <strong>冲突关系：</strong>{globalRelationshipData.relationship_stats?.conflict_relationships || 0}
              </div>
              <div>
                <strong>合作关系：</strong>{globalRelationshipData.relationship_stats?.cooperation_relationships || 0}
              </div>
            </div>

            <h3>个人关系视角</h3>
            {globalRelationshipData.perspectives && Object.keys(globalRelationshipData.perspectives).length > 0 ? (
              <div>
                {Object.entries(globalRelationshipData.perspectives).map(([characterId, perspective]: [string, any]) => {
                  const character = globalRelationshipData.characters.find((c: any) => c.id === characterId);
                  return (
                    <div key={characterId} style={{ marginBottom: '16px', padding: '12px', border: '1px solid #f0f0f0', borderRadius: '6px' }}>
                      <h4>{character?.name || '未知角色'}</h4>
                      <div style={{ 
                        lineHeight: '1.6', 
                        color: '#333',
                        fontSize: '14px',
                        whiteSpace: 'pre-wrap'
                      }}>
                        {perspective}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ color: '#999' }}>暂无个人关系视角</div>
            )}
          </div>
        </Modal>
      )}

    </div>
  );
};

export default Character;
