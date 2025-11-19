import React, { useState, useEffect } from 'react';
import { 
  Card, Button, Input, message, Spin, Typography, Space, 
  Table, Select, Modal, Form, Drawer, Tag, Row, Col, 
  Statistic, Empty, Alert, Tabs, Progress
} from 'antd';
import { 
  PlayCircleOutlined, PlayCircleFilled, DeleteOutlined,
  SearchOutlined, FilterOutlined, PlusOutlined, 
  EditOutlined, EyeOutlined, StarOutlined
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface PlotOutline {
  id: string;
  title: string;
  description: string;
  theme: string;
  tone: string;
  target_word_count: number;
  estimated_chapters: number;
}

interface ChapterOutline {
  id: string;
  title: string;
  chapter_summary: string;
  act_belonging: string;
  emotional_tone: string;
  estimated_word_count: number;
  tension_level: string;
  status: string;
}

interface DetailedPlot {
  id: string;
  chapter_outline_id: string;
  plot_outline_id: string;
  title: string;
  content: string;
  word_count: number;
  status: string;
  logic_check_result?: any;
  logic_status?: string;
  scoring_status?: string;
  total_score?: number;
  scoring_result?: any;
  scoring_feedback?: string;
  scored_at?: string;
  scored_by?: string;
  created_at: string;
  updated_at: string;
}

const DetailedPlot: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [plotOutlines, setPlotOutlines] = useState<PlotOutline[]>([]);
  const [chapterOutlines, setChapterOutlines] = useState<ChapterOutline[]>([]);
  const [detailedPlots, setDetailedPlots] = useState<DetailedPlot[]>([]);
  const [selectedPlotOutline, setSelectedPlotOutline] = useState<string>('');
  const [selectedChapterOutline, setSelectedChapterOutline] = useState<string>('');
  const [searchText, setSearchText] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showDetailDrawer, setShowDetailDrawer] = useState(false);
  const [selectedDetailedPlot, setSelectedDetailedPlot] = useState<DetailedPlot | null>(null);
  const [generateForm] = Form.useForm();
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [logicCheckModalVisible, setLogicCheckModalVisible] = useState(false);
  const [logicCheckResult, setLogicCheckResult] = useState<any>(null);
  const [checkingLogic, setCheckingLogic] = useState<Set<string>>(new Set());
  const [scoringModalVisible, setScoringModalVisible] = useState(false);
  const [scoringResult, setScoringResult] = useState<any>(null);
  const [scoring, setScoring] = useState<Set<string>>(new Set());
  const [evolutionModalVisible, setEvolutionModalVisible] = useState(false);
  const [evolutionResult, setEvolutionResult] = useState<any>(null);
  const [evolution, setEvolution] = useState<Set<string>>(new Set());
  const [evolutionTypes, setEvolutionTypes] = useState<any[]>([]);
  const [selectedEvolutionType, setSelectedEvolutionType] = useState<string>('general');
  const [evolutionPrompt, setEvolutionPrompt] = useState(''); // 新增：进化描述输入
  const [showEvolutionConfirm, setShowEvolutionConfirm] = useState(false); // 新增：控制确认/结果状态
  const [latestScoringData, setLatestScoringData] = useState<any>(null); // 新增：最新评分数据
  const [correctionModalVisible, setCorrectionModalVisible] = useState(false);
  const [correctionResult, setCorrectionResult] = useState<any>(null);
  const [correcting, setCorrecting] = useState<Set<string>>(new Set());
  const [correctionPrompt, setCorrectionPrompt] = useState('');
  const [correctionHistory, setCorrectionHistory] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  
  // 编辑功能相关状态
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editForm] = Form.useForm();
  const [editingDetailedPlot, setEditingDetailedPlot] = useState<DetailedPlot | null>(null);

  // 获取剧情大纲列表
  const fetchPlotOutlines = async () => {
    try {
      console.log('开始获取剧情大纲...');
      const response = await fetch('http://localhost:8001/api/v1/plot/plot-outlines');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Plot outlines API response:', {
        status: response.status,
        data: data,
        dataLength: data?.length || 0
      });
      
      // 确保data是数组
      if (Array.isArray(data)) {
        setPlotOutlines(data);
        console.log('剧情大纲加载成功:', data.length, '个');
      } else {
        console.error('数据结构错误，期望数组，实际:', typeof data);
        setPlotOutlines([]);
        message.warning('剧情大纲数据格式错误');
      }
    } catch (error) {
      console.error('获取剧情大纲失败:', error);
      setPlotOutlines([]);
      message.error(`获取剧情大纲失败: ${error.message}`);
    }
  };

  // 获取章节大纲列表
  const fetchChapterOutlines = async (plotOutlineId: string) => {
    if (!plotOutlineId) return;
    
    try {
      const response = await fetch(`http://localhost:8001/api/v1/chapter/chapter-outlines/${plotOutlineId}`);
      const data = await response.json();
      console.log('Chapter outlines data:', data);
      setChapterOutlines(data || []);
    } catch (error) {
      console.error('获取章节大纲失败:', error);
      message.error('获取章节大纲失败');
    }
  };

  // 获取详细剧情列表
  const fetchDetailedPlots = async (plotOutlineId: string, pageNum: number = 1) => {
    if (!plotOutlineId) {
      console.log('No plot outline selected, skipping fetch');
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8001/api/v1/detailed-plots/${plotOutlineId}?page=${pageNum}&page_size=${pageSize}`);
      const data = await response.json();
      console.log('Detailed plots data:', data);
      console.log('Detailed plots with logic status:', data.detailed_plots?.map((plot: any) => ({
        id: plot.id,
        title: plot.title,
        logic_status: plot.logic_status,
        logic_score: plot.logic_score
      })));
      setDetailedPlots(data.detailed_plots || []);
      setTotal(data.total || 0);
    } catch (error) {
      console.error('获取详细剧情失败:', error);
      message.error('获取详细剧情失败');
    }
  };

  // 生成详细剧情
  const handleGenerateDetailedPlot = async () => {
    try {
      const values = await generateForm.validateFields();
      
      // 获取选中的章节信息
      const selectedChapter = chapterOutlines.find(chapter => chapter.id === values.chapter_outline_id);
      if (!selectedChapter) {
        message.error('未找到选中的章节');
        return;
      }
      
      setLoading(true);
      const response = await fetch('http://localhost:8001/api/v1/detailed-plots', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chapter_outline_id: values.chapter_outline_id,
          plot_outline_id: selectedPlotOutline,
          title: selectedChapter.title, // 使用章节标题
          additional_requirements: values.additional_requirements || ''
        }),
      });

      if (!response.ok) {
        throw new Error('生成失败');
      }

      const data = await response.json();
      message.success('详细剧情生成成功！');
      setShowGenerateModal(false);
      generateForm.resetFields();
      
      // 刷新列表
      fetchDetailedPlots(selectedPlotOutline, page);
    } catch (error) {
      message.error(`生成失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 查看详细剧情
  const handleViewDetailedPlot = (detailedPlot: DetailedPlot) => {
    setSelectedDetailedPlot(detailedPlot);
    setShowDetailDrawer(true);
  };

  // 删除详细剧情
  const handleDeleteDetailedPlot = async (detailedPlotId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个详细剧情吗？',
      onOk: async () => {
        try {
          const response = await fetch(`http://localhost:8001/api/v1/detailed-plots/${detailedPlotId}`, {
            method: 'DELETE',
          });

          if (!response.ok) {
            throw new Error('删除失败');
          }

          message.success('删除成功');
          fetchDetailedPlots(selectedPlotOutline, page);
        } catch (error) {
          message.error(`删除失败: ${error.message}`);
        }
      },
    });
  };

  // 逻辑检查
  const handleLogicCheck = async (detailedPlotId: string) => {
    // 添加到检查中的列表
    setCheckingLogic(prev => new Set(prev).add(detailedPlotId));
    
    try {
      const response = await fetch(`http://localhost:8001/api/v1/detailed-plots/${detailedPlotId}/logic-check`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('逻辑检查失败');
      }

      const result = await response.json();
      console.log('逻辑检查结果:', result);
      setLogicCheckResult(result.logic_result);
      setLogicCheckModalVisible(true);
      message.success('逻辑检查完成');
      
      // 刷新列表以显示更新后的状态
      if (selectedPlotOutline) {
        console.log('Refreshing detailed plots for plot outline:', selectedPlotOutline);
        await fetchDetailedPlots(selectedPlotOutline, page);
        console.log('详细剧情列表已刷新');
      } else {
        console.log('No plot outline selected, cannot refresh detailed plots');
      }
    } catch (error) {
      message.error(`逻辑检查失败: ${error.message}`);
    } finally {
      // 从检查中的列表移除
      setCheckingLogic(prev => {
        const newSet = new Set(prev);
        newSet.delete(detailedPlotId);
        return newSet;
      });
    }
  };

  // 评分智能体
  const handleScoring = async (detailedPlotId: string) => {
    // 找到对应的详细剧情记录
    const plotRecord = detailedPlots.find(plot => plot.id === detailedPlotId);
    if (!plotRecord) {
      message.error('找不到对应的详细剧情记录');
      return;
    }

    // 添加到评分中的列表
    setScoring(prev => new Set(prev).add(detailedPlotId));
    
    try {
      const response = await fetch(`http://localhost:8001/api/v1/score-intelligent/detailed-plots/${detailedPlotId}/scoring`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          detailed_plot_id: detailedPlotId,
          content: plotRecord.content // 传递详细剧情内容
        }),
      });

      if (!response.ok) {
        throw new Error('智能评分失败');
      }

      const result = await response.json();
      console.log('评分结果:', result);
      
      // 使用新的评分结果格式
      setScoringResult(result.scoring_result);
      setScoringModalVisible(true);
      message.success('智能评分完成');
      
      // 刷新列表以显示更新后的状态
      if (selectedPlotOutline) {
        console.log('Refreshing detailed plots for plot outline:', selectedPlotOutline);
        await fetchDetailedPlots(selectedPlotOutline, page);
        console.log('详细剧情列表已刷新');
      } else {
        console.log('No plot outline selected, cannot refresh detailed plots');
      }
    } catch (error) {
      message.error(`智能评分失败: ${error.message}`);
    } finally {
      // 从评分中的列表移除
      setScoring(prev => {
        const newSet = new Set(prev);
        newSet.delete(detailedPlotId);
        return newSet;
      });
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      ellipsis: true,
    },
    {
      title: '字数',
      dataIndex: 'word_count',
      key: 'word_count',
      width: 80,
      render: (wordCount: number) => wordCount.toLocaleString(),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const color = status === '已完成' ? 'green' : status === '草稿' ? 'orange' : 'blue';
        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: '逻辑状态',
      dataIndex: 'logic_status',
      key: 'logic_status',
      width: 100,
      render: (logicStatus: string, record: DetailedPlot) => {
        if (!logicStatus) {
          return <Tag color="default">未检查</Tag>;
        }
        const color = logicStatus === '通过' ? 'green' : 
                     logicStatus === '警告' ? 'orange' : 
                     logicStatus === '未通过' ? 'red' : 'blue';
        return <Tag color={color}>{logicStatus}</Tag>;
      },
    },
    {
      title: '评分状态',
      dataIndex: 'scoring_status',
      key: 'scoring_status',
      width: 100,
      render: (scoringStatus: string, record: DetailedPlot) => {
        if (!scoringStatus || scoringStatus === '未评分') {
          return <Tag color="default">未评分</Tag>;
        }
        const color = scoringStatus === '已完成' ? 'green' : 
                     scoringStatus === '评分中' ? 'blue' : 
                     scoringStatus === '评分失败' ? 'red' : 'default';
        return <Tag color={color}>{scoringStatus}</Tag>;
      },
    },
    {
      title: '智能评分',
      dataIndex: 'total_score',
      key: 'total_score',
      width: 80,
      render: (score: number) => {
        if (score === null || score === undefined) return '-';
        const color = score >= 90 ? 'green' : score >= 80 ? 'blue' : score >= 70 ? 'orange' : score >= 60 ? 'yellow' : 'red';
        return <Tag color={color}>{score.toFixed(1)}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record: DetailedPlot) => (
        <Space>
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => handleViewDetailedPlot(record)}
          >
            查看
          </Button>
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => handleEditDetailedPlot(record)}
            style={{ color: '#1890ff' }}
          >
            编辑
          </Button>
          <Button 
            type="link" 
            loading={checkingLogic.has(record.id)}
            onClick={() => handleLogicCheck(record.id)}
          >
            逻辑检查
          </Button>
          <Button 
            type="link" 
            loading={scoring.has(record.id)}
            onClick={() => handleScoring(record.id)}
            style={{ color: '#52c41a' }}
          >
            评分智能体
          </Button>
          <Button 
            type="link" 
            loading={evolution.has(record.id)}
            onClick={() => handleEvolution(record.id)}
            style={{ color: '#1890ff' }}
          >
            进化智能体
          </Button>
          {record.logic_status && record.logic_status !== '通过' && (
            <Button 
              type="link" 
              loading={correcting.has(record.id)}
              onClick={() => handleCorrection(record.id)}
              style={{ color: '#ff4d4f' }}
            >
              修正智能体
            </Button>
          )}
          <Button 
            type="link" 
            danger
            icon={<DeleteOutlined />} 
            onClick={() => handleDeleteDetailedPlot(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  // 过滤数据
  const filteredDetailedPlots = detailedPlots.filter(plot => {
    const matchesSearch = !searchText || 
      plot.title.toLowerCase().includes(searchText.toLowerCase());
    const matchesStatus = !filterStatus || plot.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  // 获取进化类型
  const fetchEvolutionTypes = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/evolution-types');
      const data = await response.json();
      setEvolutionTypes(data.evolution_types || []);
    } catch (error) {
      console.error('获取进化类型失败:', error);
    }
  };

  // 获取最新评分数据
  const fetchLatestScoring = async (detailedPlotId: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/v1/score-intelligent/detailed-plots/${detailedPlotId}/scoring`);
      if (response.ok) {
        const result = await response.json();
        return result.scoring_result;
      }
    } catch (error) {
      console.error('获取评分数据失败:', error);
    }
    return null;
  };

  // 进化智能体 - 显示确认弹窗
  const handleEvolution = async (detailedPlotId: string) => {
    setSelectedDetailedPlot(detailedPlots.find(plot => plot.id === detailedPlotId) || null);
    
    // 获取最新评分数据
    const scoringData = await fetchLatestScoring(detailedPlotId);
    setLatestScoringData(scoringData);
    
    setEvolutionModalVisible(true);
    setEvolutionResult(null); // Clear previous result when opening confirmation
    setEvolutionPrompt(''); // Clear previous prompt
    setShowEvolutionConfirm(true); // Show confirmation state
  };

  // 确认进化
  const handleConfirmEvolution = async () => {
    if (!selectedDetailedPlot) return;
    
    const detailedPlotId = selectedDetailedPlot.id;
    setEvolution(prev => new Set(prev).add(detailedPlotId));
    
    try {
      const response = await fetch(`http://localhost:8001/api/v1/detailed-plots/${detailedPlotId}/evolution?evolution_type=${selectedEvolutionType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          evolution_prompt: evolutionPrompt // Send user prompt to backend
        }),
      });

      if (!response.ok) {
        throw new Error('智能进化失败');
      }

      const result = await response.json();
      console.log('进化结果:', result);
      setEvolutionResult(result.evolution_result);
      setShowEvolutionConfirm(false); // Switch to result state
      message.success('智能进化完成');
      
      // 刷新列表以显示更新后的状态
      if (selectedPlotOutline) {
        console.log('Refreshing detailed plots for plot outline:', selectedPlotOutline);
        await fetchDetailedPlots(selectedPlotOutline, page);
        console.log('详细剧情列表已刷新');
      } else {
        console.log('No plot outline selected, cannot refresh detailed plots');
      }
    } catch (error) {
      message.error(`智能进化失败: ${error.message}`);
    } finally {
      // 从进化中的_list移除
      setEvolution(prev => {
        const newSet = new Set(prev);
        newSet.delete(detailedPlotId);
        return newSet;
      });
    }
  };

  // 获取修正历史
  const fetchCorrectionHistory = async (detailedPlotId: string) => {
    setLoadingHistory(true);
    try {
      console.log('获取修正历史，detailedPlotId:', detailedPlotId);
      const response = await fetch(`http://localhost:8001/api/v1/detailed-plots/${detailedPlotId}/correction-history`);
      if (response.ok) {
        const data = await response.json();
        console.log('修正历史数据:', data);
        setCorrectionHistory(data.correction_history || []);
      } else {
        console.error('获取修正历史失败:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('获取修正历史失败:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  // 编辑详细剧情
  const handleEditDetailedPlot = (detailedPlot: DetailedPlot) => {
    setEditingDetailedPlot(detailedPlot);
    editForm.setFieldsValue({
      title: detailedPlot.title,
      content: detailedPlot.content
    });
    setEditModalVisible(true);
  };

  // 保存编辑
  const handleSaveEdit = async () => {
    if (!editingDetailedPlot) return;
    
    try {
      const values = await editForm.validateFields();
      
      const response = await fetch(`http://localhost:8001/api/v1/detailed-plots/${editingDetailedPlot.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: values.title,
          content: values.content,
          word_count: values.content.length
        }),
      });

      if (!response.ok) {
        throw new Error('更新失败');
      }

      message.success('详细剧情更新成功！');
      setEditModalVisible(false);
      editForm.resetFields();
      
      // 刷新列表
      if (selectedPlotOutline) {
        await fetchDetailedPlots(selectedPlotOutline, page);
      }
    } catch (error: any) {
      message.error(`更新失败: ${error.message}`);
    }
  };

  // 修正智能体 - 显示确认弹窗
  const handleCorrection = (detailedPlotId: string) => {
    setSelectedDetailedPlot(detailedPlots.find(plot => plot.id === detailedPlotId) || null);
    setCorrectionModalVisible(true);
    // 获取修正历史
    fetchCorrectionHistory(detailedPlotId);
  };

  // 确认修正
  const handleConfirmCorrection = async () => {
    if (!selectedDetailedPlot) return;
    
    const detailedPlotId = selectedDetailedPlot.id;
    // 添加到修正中的列表
    setCorrecting(prev => new Set(prev).add(detailedPlotId));
    
    try {
      const response = await fetch(`http://localhost:8001/api/v1/detailed-plots/${detailedPlotId}/correction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          correction_prompt: correctionPrompt
        }),
      });

      if (!response.ok) {
        throw new Error('智能修正失败');
      }

      const result = await response.json();
      console.log('修正结果:', result);
      setCorrectionResult(result.correction_result);
      message.success('智能修正完成');
      
      // 刷新修正历史
      await fetchCorrectionHistory(detailedPlotId);
      
      // 刷新列表以显示更新后的状态
      if (selectedPlotOutline) {
        console.log('Refreshing detailed plots for plot outline:', selectedPlotOutline);
        await fetchDetailedPlots(selectedPlotOutline, page);
        console.log('详细剧情列表已刷新');
      } else {
        console.log('No plot outline selected, cannot refresh detailed plots');
      }
    } catch (error) {
      message.error(`智能修正失败: ${error.message}`);
    } finally {
      // 从修正中的列表移除
      setCorrecting(prev => {
        const newSet = new Set(prev);
        newSet.delete(detailedPlotId);
        return newSet;
      });
    }
  };

  // 初始化
  useEffect(() => {
    fetchPlotOutlines();
    fetchEvolutionTypes();
  }, []);

  // 当选择剧情大纲时，获取章节大纲
  useEffect(() => {
    if (selectedPlotOutline) {
      fetchChapterOutlines(selectedPlotOutline);
      fetchDetailedPlots(selectedPlotOutline, 1);
      setPage(1);
    }
  }, [selectedPlotOutline]);

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <PlayCircleFilled style={{ marginRight: 8 }} />
          详细剧情管理
        </Title>
        <Paragraph style={{ fontSize: 16, color: '#666' }}>
          基于章节大纲生成详细的剧情内容，包含对话、动作和场景描述。
        </Paragraph>
      </div>

      {/* 剧情大纲选择 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={12}>
            <Text strong>选择剧情大纲：</Text>
            <Select
              placeholder="请选择剧情大纲"
              value={selectedPlotOutline}
              onChange={(value) => {
                setSelectedPlotOutline(value);
                setSelectedChapterOutline('');
              }}
              style={{ width: '100%', marginTop: 8 }}
              showSearch
              filterOption={(input, option) =>
                (option?.children as string)?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {plotOutlines.length === 0 ? (
                <Option key="no-data" value="" disabled>
                  暂无剧情大纲（检查网络连接和API）
                </Option>
              ) : (
                plotOutlines.map((plot) => (
                  <Option key={plot.id} value={plot.id}>
                    {plot.title}
                  </Option>
                ))
              )}
            </Select>
          </Col>
          <Col span={12}>
            <div style={{ textAlign: 'right', marginTop: 8 }}>
              <Space>
                <Select
                  placeholder="选择进化类型"
                  value={selectedEvolutionType}
                  onChange={setSelectedEvolutionType}
                  style={{ width: 150 }}
                >
                  {evolutionTypes.map((type) => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setShowGenerateModal(true)}
                  disabled={!selectedPlotOutline}
                >
                  生成详细剧情
                </Button>
              </Space>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 统计信息 */}
      {selectedPlotOutline && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card>
              <Statistic title="总数量" value={total} />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic title="已过滤" value={filteredDetailedPlots.length} />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic 
                title="已完成" 
                value={detailedPlots.filter(p => p.status === '已完成').length} 
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 搜索和筛选 */}
      {selectedPlotOutline && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={8}>
            <Input
              placeholder="搜索详细剧情标题"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              allowClear
            />
          </Col>
          <Col span={6}>
            <Select
              placeholder="按状态筛选"
              value={filterStatus}
              onChange={setFilterStatus}
              allowClear
              style={{ width: '100%' }}
            >
              <Option value="草稿">草稿</Option>
              <Option value="已完成">已完成</Option>
              <Option value="已发布">已发布</Option>
            </Select>
          </Col>
          <Col span={6}>
            <Button
              icon={<FilterOutlined />}
              onClick={() => {
                setSearchText('');
                setFilterStatus('');
              }}
            >
              清除筛选
            </Button>
          </Col>
        </Row>
      )}

      {/* 详细剧情列表 */}
      {selectedPlotOutline ? (
        <Card>
          <div style={{ maxHeight: '70vh', overflow: 'auto' }}>
            <Table
              columns={columns}
              dataSource={filteredDetailedPlots}
              rowKey="id"
              pagination={{
                current: page,
                pageSize: pageSize,
                total: total,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
                onChange: (pageNum, size) => {
                  setPage(pageNum);
                  setPageSize(size);
                  fetchDetailedPlots(selectedPlotOutline, pageNum);
                },
              }}
              loading={loading}
              scroll={{ x: 1200 }}
            />
          </div>
        </Card>
      ) : (
        <Card>
          <Empty 
            description="请先选择一个剧情大纲"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </Card>
      )}

      {/* 生成详细剧情模态框 */}
      <Modal
        title="生成详细剧情"
        open={showGenerateModal}
        onOk={handleGenerateDetailedPlot}
        onCancel={() => {
          setShowGenerateModal(false);
          generateForm.resetFields();
        }}
        confirmLoading={loading}
        width={600}
      >
        <Form form={generateForm} layout="vertical">
          <Form.Item
            name="chapter_outline_id"
            label="选择章节"
            rules={[{ required: true, message: '请选择章节' }]}
          >
            <Select 
              placeholder="请选择章节"
              onChange={(value) => {
                const selectedChapter = chapterOutlines.find(chapter => chapter.id === value);
                if (selectedChapter) {
                  // 更新表单中的章节描述显示
                  generateForm.setFieldsValue({
                    chapter_description: selectedChapter.chapter_summary
                  });
                }
              }}
            >
              {chapterOutlines.map((chapter) => (
                <Option key={chapter.id} value={chapter.id}>
                  {chapter.title}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="chapter_description"
            label="章节描述"
          >
            <TextArea 
              placeholder="选择章节后将显示章节描述"
              rows={4}
              readOnly
              style={{ backgroundColor: '#f5f5f5' }}
            />
          </Form.Item>
          
          <Form.Item
            name="additional_requirements"
            label="额外要求"
          >
            <TextArea 
              placeholder="请输入额外的生成要求（可选）"
              rows={3}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 详细剧情查看抽屉 */}
      <Drawer
        title={selectedDetailedPlot?.title}
        placement="right"
        width={800}
        open={showDetailDrawer}
        onClose={() => setShowDetailDrawer(false)}
      >
        {selectedDetailedPlot && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <Text strong>字数：</Text>
                <Text>{selectedDetailedPlot.word_count.toLocaleString()}</Text>
              </Col>
              <Col span={8}>
                <Text strong>状态：</Text>
                <Tag color={selectedDetailedPlot.status === '已完成' ? 'green' : 'orange'}>
                  {selectedDetailedPlot.status}
                </Tag>
              </Col>
              <Col span={8}>
                <Text strong>创建时间：</Text>
                <Text>{new Date(selectedDetailedPlot.created_at).toLocaleString()}</Text>
              </Col>
            </Row>
            
            <div style={{ 
              background: '#f5f5f5', 
              padding: 16, 
              borderRadius: 8,
              whiteSpace: 'pre-wrap',
              maxHeight: 600,
              overflow: 'auto'
            }}>
              {selectedDetailedPlot.content}
            </div>
          </div>
        )}
      </Drawer>

      {/* 逻辑检查结果Modal */}
      <Modal
        title="逻辑检查结果"
        open={logicCheckModalVisible}
        onCancel={() => setLogicCheckModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setLogicCheckModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {logicCheckResult && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <Statistic 
                  title="整体状态" 
                  value={logicCheckResult.overall_status}
                  valueStyle={{ 
                    color: logicCheckResult.overall_status === '通过' ? '#3f8600' : 
                           logicCheckResult.overall_status === '警告' ? '#faad14' : '#cf1322'
                  }}
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="逻辑分数" 
                  value={logicCheckResult.logic_score} 
                  precision={1}
                  suffix="/ 100"
                  valueStyle={{ 
                    color: logicCheckResult.logic_score >= 80 ? '#3f8600' : 
                           logicCheckResult.logic_score >= 60 ? '#faad14' : '#cf1322'
                  }}
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="问题数量" 
                  value={logicCheckResult.issues_found?.length || 0}
                  valueStyle={{ 
                    color: (logicCheckResult.issues_found?.length || 0) === 0 ? '#3f8600' : '#cf1322'
                  }}
                />
              </Col>
            </Row>

            {logicCheckResult.summary && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>检查总结：</Text>
                <div style={{ marginTop: 8, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                  {logicCheckResult.summary}
                </div>
              </div>
            )}

            {logicCheckResult.dimension_scores && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>各维度评分：</Text>
                <Row gutter={8} style={{ marginTop: 8 }}>
                  {Object.entries(logicCheckResult.dimension_scores).map(([dimension, score]) => (
                    <Col key={dimension} span={6}>
                      <Tag color={score >= 80 ? 'green' : score >= 60 ? 'orange' : 'red'}>
                        {dimension}: {score.toFixed(1)}
                      </Tag>
                    </Col>
                  ))}
                </Row>
              </div>
            )}

            {logicCheckResult.issues_found && logicCheckResult.issues_found.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>发现的问题：</Text>
                <div style={{ marginTop: 8, maxHeight: 300, overflow: 'auto' }}>
                  {logicCheckResult.issues_found.map((issue: any, index: number) => (
                    <Card key={index} size="small" style={{ marginBottom: 8 }}>
                      <div style={{ marginBottom: 4 }}>
                        <Tag color={issue.severity === '高' ? 'red' : issue.severity === '中' ? 'orange' : 'blue'}>
                          {issue.severity}
                        </Tag>
                        <Tag color="purple">{issue.category}</Tag>
                        {issue.location && <Text type="secondary">位置: {issue.location}</Text>}
                      </div>
                      <div style={{ marginBottom: 4 }}>
                        <Text strong>问题：</Text>
                        <Text>{issue.description}</Text>
                      </div>
                      {issue.suggestion && (
                        <div>
                          <Text strong>建议：</Text>
                          <Text type="secondary">{issue.suggestion}</Text>
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {logicCheckResult.recommendations && logicCheckResult.recommendations.length > 0 && (
              <div>
                <Text strong>改进建议：</Text>
                <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                  {logicCheckResult.recommendations.map((rec: string, index: number) => (
                    <li key={index} style={{ marginBottom: 4 }}>
                      <Text>{rec}</Text>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* 评分结果弹窗 */}
      <Modal
        title="智能评分结果"
        open={scoringModalVisible}
        onCancel={() => setScoringModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setScoringModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={1000}
      >
        {scoringResult && (
          <div>
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Statistic 
                  title="总分" 
                  value={scoringResult.total_score} 
                  precision={1}
                  suffix="/ 100"
                  valueStyle={{ 
                    color: scoringResult.total_score >= 90 ? '#3f8600' : 
                           scoringResult.total_score >= 80 ? '#1890ff' : 
                           scoringResult.total_score >= 70 ? '#faad14' : 
                           scoringResult.total_score >= 60 ? '#fa8c16' : '#cf1322'
                  }}
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="评分等级" 
                  value={scoringResult.total_score >= 90 ? '优秀' : 
                         scoringResult.total_score >= 80 ? '良好' : 
                         scoringResult.total_score >= 70 ? '一般' : 
                         scoringResult.total_score >= 60 ? '较差' : '很差'}
                  valueStyle={{ 
                    color: scoringResult.total_score >= 90 ? '#3f8600' : 
                           scoringResult.total_score >= 80 ? '#1890ff' : 
                           scoringResult.total_score >= 70 ? '#faad14' : 
                           scoringResult.total_score >= 60 ? '#fa8c16' : '#cf1322'
                  }}
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="评分时间" 
                  value={new Date(scoringResult.scored_at).toLocaleString()}
                />
              </Col>
            </Row>

            {/* 各维度分数 */}
            {scoringResult.scores && (
              <div style={{ marginBottom: 24 }}>
                <Text strong style={{ fontSize: 16, marginBottom: 16, display: 'block' }}>
                  各维度详细评分：
                </Text>
                {Object.entries(scoringResult.scores).map(([dimension, score]: [string, any]) => {
                  const dimensionNames: { [key: string]: string } = {
                    'logic_consistency': '逻辑自洽性',
                    'dramatic_conflict': '戏剧冲突性',
                    'character_development': '角色发展性',
                    'world_usage': '世界观运用',
                    'writing_style': '文笔风格',
                    'dramatic_tension': '戏剧张力',
                    'emotional_impact': '情感冲击',
                    'thematic_depth': '主题深度',
                    'pacing_fluency': '节奏与流畅度',
                    'originality_creativity': '新颖性与创意'
                  };
                  
                  const dimensionColors: { [key: string]: string } = {
                    'logic_consistency': '#1890ff',
                    'dramatic_conflict': '#52c41a',
                    'character_development': '#fa8c16',
                    'world_usage': '#722ed1',
                    'writing_style': '#eb2f96',
                    'dramatic_tension': '#1890ff',
                    'emotional_impact': '#52c41a',
                    'thematic_depth': '#722ed1',
                    'pacing_fluency': '#eb2f96',
                    'originality_creativity': '#fa8c16'
                  };
                  
                  const color = dimensionColors[dimension] || '#1890ff';
                  const name = dimensionNames[dimension] || dimension;
                  
                  return (
                    <Card 
                      key={dimension} 
                      size="small" 
                      style={{ marginBottom: 12, border: `1px solid ${color}20` }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                            <StarOutlined style={{ color, marginRight: 8 }} />
                            <span style={{ fontWeight: 'bold', fontSize: 16 }}>
                              {name}
                            </span>
                          </div>
                        </div>
                        
                        <div style={{ width: 300, marginLeft: 16 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <span style={{ fontSize: 18, fontWeight: 'bold', color }}>
                              {score.toFixed(1)}分
                            </span>
                            <span style={{ color: '#666' }}>
                              {score >= 90 ? '优秀' : 
                               score >= 80 ? '良好' : 
                               score >= 70 ? '一般' : 
                               score >= 60 ? '较差' : '很差'}
                            </span>
                          </div>
                          <Progress 
                            percent={score} 
                            strokeColor={color}
                            showInfo={false}
                          />
                          </div>
                        </div>
                      </Card>
                  );
                })}
              </div>
            )}

            {/* 详细反馈 */}
            {scoringResult.detailed_feedback && (
              <div style={{ marginBottom: 16 }}>
                <Text strong style={{ fontSize: 16, marginBottom: 16, display: 'block' }}>
                  各维度详细反馈：
                      </Text>
                {Object.entries(scoringResult.detailed_feedback).map(([dimension, feedback]: [string, any]) => {
                  const dimensionNames: { [key: string]: string } = {
                    'logic_consistency': '逻辑自洽性',
                    'dramatic_conflict': '戏剧冲突性',
                    'character_development': '角色发展性',
                    'world_usage': '世界观运用',
                    'writing_style': '文笔风格',
                    'dramatic_tension': '戏剧张力',
                    'emotional_impact': '情感冲击',
                    'thematic_depth': '主题深度',
                    'pacing_fluency': '节奏与流畅度',
                    'originality_creativity': '新颖性与创意'
                  };
                  
                  const name = dimensionNames[dimension] || dimension;
                  
                  return (
                    <Card key={dimension} size="small" style={{ marginBottom: 12 }}>
                      <div style={{ marginBottom: 8 }}>
                        <Text strong style={{ color: '#1890ff', fontSize: 14 }}>
                          {name}分析：
                        </Text>
                    </div>
                      <div style={{ color: '#666', lineHeight: '1.6' }}>
                        {feedback}
                </div>
                    </Card>
                  );
                })}
              </div>
            )}

            {/* 总体评价 */}
            {scoringResult.overall_feedback && (
              <div style={{ marginBottom: 16 }}>
                <Text strong style={{ fontSize: 16, marginBottom: 16, display: 'block' }}>
                  总体评价：
                </Text>
                <div style={{ marginTop: 8, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                  {scoringResult.overall_feedback}
                </div>
              </div>
            )}

            {/* 改进建议 */}
            {scoringResult.improvement_suggestions && scoringResult.improvement_suggestions.length > 0 && (
              <div>
                <Text strong style={{ fontSize: 16, marginBottom: 16, display: 'block' }}>
                  改进建议：
                </Text>
                <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                  {scoringResult.improvement_suggestions.map((suggestion: string, index: number) => (
                    <li key={index} style={{ marginBottom: 4 }}>
                      <Text>{suggestion}</Text>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* 进化结果弹窗 */}
      <Modal
        title={showEvolutionConfirm ? "" : "智能进化结果"}
        open={evolutionModalVisible}
        onCancel={() => {
          setEvolutionModalVisible(false);
          setEvolutionResult(null);
          setEvolutionPrompt(''); // Clear prompt on cancel
          setShowEvolutionConfirm(false);
        }}
        footer={showEvolutionConfirm ? [
          <Button key="cancel" onClick={() => setEvolutionModalVisible(false)}>
            取消
          </Button>,
          <Button 
            key="confirm" 
            type="primary" 
            loading={selectedDetailedPlot && evolution.has(selectedDetailedPlot.id)}
            onClick={handleConfirmEvolution}
          >
            确认进化
          </Button>
        ] : [
          <Button key="close" onClick={() => {
            setEvolutionModalVisible(false);
            setEvolutionResult(null);
            setEvolutionPrompt(''); // Clear prompt on close
            setShowEvolutionConfirm(false);
          }}>
            关闭
          </Button>
        ]}
        width={1000}
      >
        {showEvolutionConfirm ? (
          <div>
            {/* 上次评分结果显示 */}
            <div style={{ marginBottom: 24 }}>
              <Text strong style={{ fontSize: 16, marginBottom: 16, display: 'block' }}>
                上次评分结果（进化基准）：
              </Text>
                
                {/* 总分显示 */}
                <Row gutter={16} style={{ marginBottom: 16 }}>
                  <Col span={8}>
                    <Statistic 
                      title="总分" 
                      value={latestScoringData?.total_score || 0} 
                      precision={1}
                      suffix="/ 100"
                      valueStyle={{ 
                        color: (latestScoringData?.total_score || 0) >= 90 ? '#3f8600' : 
                               (latestScoringData?.total_score || 0) >= 80 ? '#1890ff' : 
                               (latestScoringData?.total_score || 0) >= 70 ? '#faad14' : 
                               (latestScoringData?.total_score || 0) >= 60 ? '#fa8c16' : '#cf1322'
                      }}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic 
                      title="评分等级" 
                      value={(latestScoringData?.total_score || 0) >= 90 ? '优秀' : 
                             (latestScoringData?.total_score || 0) >= 80 ? '良好' : 
                             (latestScoringData?.total_score || 0) >= 70 ? '一般' : 
                             (latestScoringData?.total_score || 0) >= 60 ? '较差' : '很差'}
                      valueStyle={{ 
                        color: (latestScoringData?.total_score || 0) >= 90 ? '#3f8600' : 
                               (latestScoringData?.total_score || 0) >= 80 ? '#1890ff' : 
                               (latestScoringData?.total_score || 0) >= 70 ? '#faad14' : 
                               (latestScoringData?.total_score || 0) >= 60 ? '#fa8c16' : '#cf1322'
                      }}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic 
                      title="进化目标维度"
                      value={selectedEvolutionType === 'general' ? '综合进化' :
                             selectedEvolutionType === 'dialogue' ? '对话优化' :
                             selectedEvolutionType === 'action' ? '动作强化' :
                             selectedEvolutionType === 'description' ? '描写美化' :
                             selectedEvolutionType === 'conflict' ? '冲突强化' :
                             selectedEvolutionType === 'character' ? '角色深化' : selectedEvolutionType}
                    />
                  </Col>
                </Row>

                {/* 各维度评分 */}
                <div style={{ marginBottom: 16 }}>
                  <Text strong style={{ fontSize: 14, marginBottom: 12, display: 'block' }}>
                    各维度评分：
                  </Text>
                  {latestScoringData?.dimensions ? (
                    latestScoringData.dimensions.map((dimensionData: any) => {
                      const dimension = dimensionData.dimension_name;
                      const score = dimensionData.score;
                      const displayName = dimensionData.dimension_display_name;
                      const color = '#1890ff'; // 使用默认颜色
                      const name = displayName;
                      
                      return (
                        <div key={dimension} style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                          <div style={{ width: 150 }}>
                            <span style={{ fontSize: 14 }}>{name}</span>
                          </div>
                          <div style={{ flex: 1, marginLeft: 16 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                              <span style={{ fontSize: 14, fontWeight: 'bold', color }}>
                                {score.toFixed(1)}分
                              </span>
                              <span style={{ color: '#666', fontSize: 12 }}>
                                {score >= 90 ? '优秀' : 
                                 score >= 80 ? '良好' : 
                                 score >= 70 ? '一般' : 
                                 score >= 60 ? '较差' : '很差'}
                              </span>
                            </div>
                            <Progress 
                              percent={score} 
                              strokeColor={color}
                              showInfo={false}
                              style={{ height: 6 }}
                            />
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div style={{ padding: 16, textAlign: 'center', color: '#999' }}>
                      暂无各维度评分数据
                    </div>
                  )}
                </div>

                {/* 详细反馈 */}
                <div style={{ marginBottom: 16 }}>
                  <Text strong style={{ fontSize: 14, marginBottom: 12, display: 'block' }}>
                    各维度详细评估：
                  </Text>
                  {latestScoringData?.dimensions ? (
                    latestScoringData.dimensions.map((dimensionData: any) => {
                      const dimension = dimensionData.dimension_name;
                      const feedback = dimensionData.feedback;
                      const name = dimensionData.dimension_display_name;
                      
                      return (
                        <Card key={dimension} size="small" style={{ marginBottom: 8 }}>
                          <div>
                            <Text strong style={{ color: '#1890ff', fontSize: 12 }}>
                              {name}：
                            </Text>
                            <div style={{ color: '#666', fontSize: 12, lineHeight: '1.5', marginTop: 4 }}>
                              {feedback.length > 100 ? feedback.substring(0, 100) + '...' : feedback}
                            </div>
                          </div>
                        </Card>
                      );
                    })
                  ) : (
                    <div style={{ padding: 16, textAlign: 'center', color: '#999' }}>
                      暂无详细评估数据
                    </div>
                  )}
                </div>
              </div>

            {/* 进化类型选择 */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 16 }}>
                <Text strong>进化类型：</Text>
                <Select
                  style={{ width: 200, marginTop: 8 }}
                  value={selectedEvolutionType}
                  onChange={setSelectedEvolutionType}
                  placeholder="选择进化类型"
                >
                  <Option value="general">综合进化</Option>
                  <Option value="dialogue">对话优化</Option>
                  <Option value="action">动作强化</Option>
                  <Option value="description">描写美化</Option>
                  <Option value="conflict">冲突强化</Option>
                  <Option value="character">角色深化</Option>
                </Select>
              </div>
            </div>

            {/* 人工进化描述 */}
            <div style={{ marginBottom: 16 }}>
              <Text strong style={{ fontSize: 16, marginBottom: 16, display: 'block' }}>
                进化要求（可选）：
              </Text>
              <Input.TextArea
                value={evolutionPrompt}
                onChange={(e) => setEvolutionPrompt(e.target.value)}
                placeholder="请描述您希望如何进化这段剧情，例如：增强情感表达、优化角色对话、强化戏剧冲突、美化描写细节等。留空则使用系统默认进化。"
                rows={4}
                style={{ marginTop: 8 }}
              />
            </div>

            {/* 进化说明 */}
            <Alert
              message="进化说明"
              description="系统将根据评分结果和您的进化要求对详细剧情进行智能进化，重点关注低分维度的提升，进化过程可能需要1-2分钟，请耐心等待。"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
          </div>
        ) : (
          // 进化结果显示
          evolutionResult && (
          <div>
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Statistic 
                  title="进化类型" 
                  value={evolutionResult.evolution_type === 'general' ? '综合进化' :
                         evolutionResult.evolution_type === 'dialogue' ? '对话优化' :
                         evolutionResult.evolution_type === 'action' ? '动作强化' :
                         evolutionResult.evolution_type === 'description' ? '描写美化' :
                         evolutionResult.evolution_type === 'conflict' ? '冲突强化' :
                         evolutionResult.evolution_type === 'character' ? '角色深化' : evolutionResult.evolution_type}
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="字数变化" 
                  value={evolutionResult.word_count_change || 0}
                  valueStyle={{ 
                    color: (evolutionResult.word_count_change || 0) > 0 ? '#3f8600' : 
                           (evolutionResult.word_count_change || 0) < 0 ? '#cf1322' : '#666'
                  }}
                  prefix={evolutionResult.word_count_change > 0 ? '+' : ''}
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="质量评分" 
                  value={evolutionResult.quality_score || 0} 
                  precision={1}
                  suffix="/ 100"
                  valueStyle={{ 
                    color: (evolutionResult.quality_score || 0) >= 90 ? '#3f8600' : 
                           (evolutionResult.quality_score || 0) >= 80 ? '#1890ff' : 
                           (evolutionResult.quality_score || 0) >= 70 ? '#faad14' : 
                           (evolutionResult.quality_score || 0) >= 60 ? '#fa8c16' : '#cf1322'
                  }}
                />
              </Col>
            </Row>

            {/* 进化总结 */}
            {evolutionResult.evolution_summary && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>进化总结：</Text>
                <div style={{ marginTop: 8, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                  {evolutionResult.evolution_summary}
                </div>
              </div>
            )}

            {/* 改进详情 */}
            {evolutionResult.improvements && Object.keys(evolutionResult.improvements).length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>改进详情：</Text>
                <div style={{ marginTop: 8 }}>
                  {Object.entries(evolutionResult.improvements).map(([dimension, feedback]: [string, any]) => (
                    <div key={dimension} style={{ marginBottom: 12, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                      <Text strong>
                        {dimension === 'dramatic_tension' ? '戏剧张力：' :
                         dimension === 'emotional_impact' ? '情感冲击：' :
                         dimension === 'character_development' ? '角色塑造：' :
                         dimension === 'thematic_depth' ? '主题深度：' :
                         dimension === 'pacing_fluency' ? '节奏与流畅度：' :
                         dimension === 'originality_creativity' ? '新颖性与创意：' : dimension + '：'}
                      </Text>
                      <div style={{ marginTop: 4 }}>{feedback}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 进化说明 */}
            {evolutionResult.evolution_notes && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>进化说明：</Text>
                <div style={{ marginTop: 8, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                  {evolutionResult.evolution_notes}
                </div>
              </div>
            )}

                    </div>
          )
        )}
      </Modal>

      {/* 修正确认/结果弹窗 */}
      <Modal
        title={correctionResult ? "智能修正结果" : "修正智能体"}
        open={correctionModalVisible}
        onCancel={() => {
          setCorrectionModalVisible(false);
          setCorrectionResult(null);
        }}
        footer={correctionResult ? [
          <Button key="close" onClick={() => {
            setCorrectionModalVisible(false);
            setCorrectionResult(null);
          }}>
            关闭
          </Button>
        ] : [
          <Button key="cancel" onClick={() => setCorrectionModalVisible(false)}>
            取消
          </Button>,
          <Button 
            key="confirm" 
            type="primary" 
            loading={selectedDetailedPlot && correcting.has(selectedDetailedPlot.id)}
            onClick={handleConfirmCorrection}
          >
            确认修正
          </Button>
        ]}
        width={1000}
      >
        {correctionResult ? (
          <Tabs 
            defaultActiveKey="result" 
            items={[
              {
                key: 'result',
                label: '修正结果',
                children: (
          <div>
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Statistic 
                  title="修正状态" 
                  value={correctionResult.correction_status === 'completed' ? '修正完成' : '修正失败'}
                  valueStyle={{ 
                    color: correctionResult.correction_status === 'completed' ? '#3f8600' : '#cf1322'
                  }}
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="字数变化" 
                  value={correctionResult.word_count_change || 0}
                  valueStyle={{ 
                    color: (correctionResult.word_count_change || 0) > 0 ? '#3f8600' : 
                           (correctionResult.word_count_change || 0) < 0 ? '#cf1322' : '#666'
                  }}
                  prefix={correctionResult.word_count_change > 0 ? '+' : ''}
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="修正时间" 
                  value={new Date().toLocaleString()}
                />
              </Col>
            </Row>

            {/* 修正总结 */}
            {correctionResult.correction_summary && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>修正总结：</Text>
                <div style={{ marginTop: 8, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                  {correctionResult.correction_summary}
                </div>
              </div>
            )}

            {/* 修正详情 */}
            {correctionResult.corrections_made && correctionResult.corrections_made.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>修正详情：</Text>
                <div style={{ marginTop: 8 }}>
                  {correctionResult.corrections_made.map((correction: any, index: number) => (
                    <div key={index} style={{ marginBottom: 12, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                      <div style={{ marginBottom: 4 }}>
                        <Tag color="blue">{correction.issue_category}</Tag>
                        <Text strong>{correction.issue_description}</Text>
                      </div>
                      <div style={{ marginBottom: 4 }}>
                        <Text strong>修正方法：</Text>
                        <Text>{correction.correction_method}</Text>
                      </div>
                      <div>
                        <Text strong>修正详情：</Text>
                        <Text>{correction.correction_details}</Text>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

                    {/* 修正备注 */}
                    {correctionResult.correction_notes && (
              <div style={{ marginBottom: 16 }}>
                        <Text strong>修正备注：</Text>
                        <div style={{ marginTop: 8, padding: 12, background: '#f0f0f0', borderRadius: 4 }}>
                          {correctionResult.correction_notes}
                </div>
              </div>
            )}

                    {/* 修正后内容 */}
              <div style={{ marginBottom: 16 }}>
                      <Text strong>修正后内容：</Text>
                      <div style={{ marginTop: 8, padding: 12, background: '#f6ffed', borderRadius: 4, border: '1px solid #b7eb8f' }}>
                        <div style={{ maxHeight: 300, overflow: 'auto', fontSize: 12, lineHeight: '1.6' }}>
                          {correctionResult.corrected_content}
                        </div>
                      </div>
                      <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                        <Text type="secondary">💡 如需查看原始内容，请在列表页面点击查看按钮</Text>
                      </div>
                    </div>
                  </div>
                )
              },
              {
                key: 'history',
                label: '修正记录',
                children: (
                  <div>
                    {loadingHistory ? (
                      <Spin tip="加载修正记录中..." />
                    ) : correctionHistory.length > 0 ? (
                      <div>
                        {correctionHistory.map((record: any, index: number) => (
                          <div key={record.id || index} style={{ marginBottom: 16 }}>
                            <div style={{ border: '1px solid #d9d9d9', borderRadius: 6, padding: 12 }}>
                              <div style={{ marginBottom: 8 }}>
                                <Space>
                                  <Tag color="blue">第{index + 1}次修正</Tag>
                                  <Tag color="green">{new Date(record.corrected_at).toLocaleString()}</Tag>
                                  <Tag color="orange">{record.corrected_by}</Tag>
                                </Space>
                              </div>
                              
                              <div style={{ marginBottom: 8 }}>
                                <Text strong>修正总结：</Text>
                                <Text style={{ marginLeft: 8 }}>{record.correction_summary}</Text>
                              </div>
                              
                              <div style={{ marginBottom: 8 }}>
                                <Text strong>字数变化：</Text>
                                <Text style={{ marginLeft: 8, color: record.word_count_change > 0 ? '#3f8600' : '#cf1322' }}>
                                  {record.word_count_change > 0 ? '+' : ''}{record.word_count_change}
                                </Text>
                              </div>
                              
                              <div style={{ marginBottom: 8 }}>
                                <Text strong>质量提升：</Text>
                                <Text style={{ marginLeft: 8 }}>{record.quality_improvement}</Text>
                              </div>
                              
                              {record.corrections_made && record.corrections_made.length > 0 && (
                                <div style={{ marginBottom: 8 }}>
                                  <Text strong>修正详情：</Text>
                                  <div style={{ marginTop: 4 }}>
                                    {record.corrections_made.map((correction: any, cIndex: number) => (
                                      <div key={cIndex} style={{ marginBottom: 4, fontSize: 12 }}>
                                        <Space>
                                          <Tag size="small">{correction.issue_category}</Tag>
                                          <Text>{correction.issue_description}</Text>
                                        </Space>
                                      </div>
                                    ))}
                </div>
              </div>
            )}

                              <div style={{ marginBottom: 8 }}>
                                <Text strong>修正内容预览：</Text>
                </div>
                              <div style={{ 
                                maxHeight: 150, 
                                overflow: 'auto', 
                                fontSize: 12, 
                                lineHeight: '1.5',
                                padding: 8,
                                background: '#f9f9f9',
                                border: '1px solid #e8e8e8',
                                borderRadius: 4
                              }}>
                                {record.corrected_content}
              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <Empty description="暂无修正记录" />
                    )}
                  </div>
                )
              }
            ]}
          />
        ) : (
          <Tabs 
            defaultActiveKey="correction" 
            items={[
              {
                key: 'correction',
                label: '确认修正',
                children: (
                  <div>
                    <div style={{ marginBottom: 16 }}>
                      <Text strong>将要修正的详细剧情：</Text>
                      <div style={{ marginTop: 8, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                        <Text strong>{selectedDetailedPlot?.title}</Text>
                        <div style={{ marginTop: 8, maxHeight: 100, overflow: 'auto', fontSize: 12 }}>
                          {selectedDetailedPlot?.content?.substring(0, 200)}
                          {(selectedDetailedPlot?.content?.length || 0) > 200 && "..."}
                        </div>
                        <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                          <Text type="secondary">💡 仅显示前200字符预览，完整内容将在修正结果中显示</Text>
                        </div>
                      </div>
                    </div>
                    
                    <Alert
                      message="修正说明"
                      description="系统将根据逻辑检查结果和您的修正要求对详细剧情进行智能修正，修正过程可能需要1-2分钟，请耐心等待。"
                      type="info"
                      showIcon
                      style={{ marginBottom: 16 }}
                    />
                    
                    {/* 逻辑检查结果 */}
                    {selectedDetailedPlot?.logic_check_result && (
                      <div style={{ marginBottom: 16 }}>
                        <Text strong>逻辑检查结果：</Text>
                        <div style={{ marginTop: 8, padding: 12, background: '#fff7e6', borderRadius: 4, border: '1px solid #ffd591' }}>
                          <div style={{ marginBottom: 8 }}>
                            <Space>
                              <Tag color={selectedDetailedPlot.logic_status === '通过' ? 'green' : 'red'}>
                                {selectedDetailedPlot.logic_status}
                              </Tag>
                              <Text strong>逻辑分数: {selectedDetailedPlot.logic_check_result.logic_score || 'N/A'}</Text>
                            </Space>
                          </div>
                          
                          {selectedDetailedPlot.logic_check_result.issues_found && selectedDetailedPlot.logic_check_result.issues_found.length > 0 && (
                            <div>
                              <Text strong>发现的问题：</Text>
                              <div style={{ marginTop: 4 }}>
                                {selectedDetailedPlot.logic_check_result.issues_found.slice(0, 3).map((issue: any, index: number) => (
                                  <div key={index} style={{ marginBottom: 4, fontSize: 12 }}>
                                    <Space>
                                      <Tag size="small" color={issue.severity === '高' ? 'red' : issue.severity === '中' ? 'orange' : 'blue'}>
                                        {issue.severity}
                                      </Tag>
                                      <Tag size="small">{issue.dimension}</Tag>
                                      <Text>{issue.description.substring(0, 80)}...</Text>
                                    </Space>
                                  </div>
                                ))}
                                {selectedDetailedPlot.logic_check_result.issues_found.length > 3 && (
                                  <Text type="secondary" style={{ fontSize: 12 }}>
                                    还有 {selectedDetailedPlot.logic_check_result.issues_found.length - 3} 个问题...
                                  </Text>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
            <div style={{ marginBottom: 16 }}>
                      <Text strong>修正要求（可选）：</Text>
                      <Input.TextArea
                        value={correctionPrompt}
                        onChange={(e) => setCorrectionPrompt(e.target.value)}
                        placeholder="请描述您希望如何修正这段剧情，例如：调整修炼进度、修改角色对话、优化情节发展等。留空则使用系统默认修正。"
                        rows={4}
                        style={{ marginTop: 8 }}
                      />
                    </div>
                    
                    <div style={{ marginBottom: 16 }}>
                      <Text strong>系统将自动修正：</Text>
                      <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                        <li>修正逻辑检查中发现的问题</li>
                        <li>保持原文的写作风格和语调</li>
                        <li>确保修正后的内容逻辑严密</li>
                        <li>优化角色行为的一致性</li>
                      </ul>
                  </div>
                    </div>
                )
              },
              {
                key: 'history',
                label: '修正记录',
                children: (
                  <div>
                    {loadingHistory ? (
                      <Spin tip="加载修正记录中..." />
                    ) : correctionHistory.length > 0 ? (
                      <div>
                        {correctionHistory.map((record: any, index: number) => (
                          <div key={record.id || index} style={{ marginBottom: 16 }}>
                            <div style={{ border: '1px solid #d9d9d9', borderRadius: 6, padding: 12 }}>
                              <div style={{ marginBottom: 8 }}>
                                <Space>
                                  <Tag color="blue">第{index + 1}次修正</Tag>
                                  <Tag color="green">{new Date(record.corrected_at).toLocaleString()}</Tag>
                                  <Tag color="orange">{record.corrected_by}</Tag>
                                </Space>
                  </div>
                              
                              <div style={{ marginBottom: 8 }}>
                                <Text strong>修正总结：</Text>
                                <Text style={{ marginLeft: 8 }}>{record.correction_summary}</Text>
                              </div>
                              
                              <div style={{ marginBottom: 8 }}>
                                <Text strong>字数变化：</Text>
                                <Text style={{ marginLeft: 8, color: record.word_count_change > 0 ? '#3f8600' : '#cf1322' }}>
                                  {record.word_count_change > 0 ? '+' : ''}{record.word_count_change}
                                </Text>
                              </div>
                              
                              <div style={{ marginBottom: 8 }}>
                                <Text strong>质量提升：</Text>
                                <Text style={{ marginLeft: 8 }}>{record.quality_improvement}</Text>
                              </div>
                              
                              {record.corrections_made && record.corrections_made.length > 0 && (
                                <div style={{ marginBottom: 8 }}>
                                  <Text strong>修正详情：</Text>
                                  <div style={{ marginTop: 4 }}>
                                    {record.corrections_made.map((correction: any, cIndex: number) => (
                                      <div key={cIndex} style={{ marginBottom: 4, fontSize: 12 }}>
                                        <Space>
                                          <Tag size="small">{correction.issue_category}</Tag>
                                          <Text>{correction.issue_description}</Text>
                                        </Space>
                                      </div>
                                    ))}
            </div>
          </div>
                              )}
                              
                              <div style={{ marginBottom: 8 }}>
                                <Text strong>修正内容预览：</Text>
                              </div>
                              <div style={{ 
                                maxHeight: 150, 
                                overflow: 'auto', 
                                fontSize: 12, 
                                lineHeight: '1.5',
                                padding: 8,
                                background: '#f9f9f9',
                                border: '1px solid #e8e8e8',
                                borderRadius: 4
                              }}>
                                {record.corrected_content}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <Empty description="暂无修正记录" />
                    )}
                  </div>
                )
              }
            ]}
          />
        )}
      </Modal>

      {/* 编辑详细剧情弹窗 */}
      <Modal
        title="编辑详细剧情"
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false);
          editForm.resetFields();
        }}
        footer={[
          <Button key="cancel" onClick={() => {
            setEditModalVisible(false);
            editForm.resetFields();
          }}>
            取消
          </Button>,
          <Button 
            key="save" 
            type="primary" 
            onClick={handleSaveEdit}
          >
            保存
          </Button>
        ]}
        width={1000}
      >
        <Form form={editForm} layout="vertical">
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="请输入详细剧情标题" />
          </Form.Item>
          
          <Form.Item
            name="content"
            label="内容"
            rules={[{ required: true, message: '请输入内容' }]}
          >
            <Input.TextArea
              placeholder="请输入详细剧情内容"
              rows={20}
              style={{ fontSize: '14px', lineHeight: '1.6' }}
            />
          </Form.Item>
          
          {editingDetailedPlot && (
            <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
              <Text type="secondary">
                💡 编辑提示：修改内容后，字数统计会自动更新。建议保持原文的写作风格和逻辑结构。
              </Text>
            </div>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default DetailedPlot;
