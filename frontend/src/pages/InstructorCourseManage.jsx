import React, { useState, useMemo, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useGetCourseQuery,
  useCreateCourseMutation,
  useUpdateCourseMutation,
  useGetModulesQuery,
  useCreateModuleMutation,
  useUpdateModuleMutation,
  useDeleteModuleMutation
} from '../services/apiSlice';
import { toast } from '../utils/toast';
import ConfirmModal from '../components/ConfirmModal';
import {
  validateTitle,
  validateDescription,
  validateCategory,
  validateModuleDescription,
  validateNumber
} from '../utils/validation';

const InstructorCourseManage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = !id || id === 'new';
  const moduleFormRef = useRef(null);


  const { data: courseData, isLoading: courseLoading } = useGetCourseQuery(
    id,
    {
      skip: isNew,
      refetchOnMountOrArgChange: true
    }
  );
  const { data: modulesData, refetch: refetchModules } = useGetModulesQuery(
    id,
    {
      skip: isNew,
      refetchOnMountOrArgChange: true
    }
  );
  const [createCourse] = useCreateCourseMutation();
  const [updateCourse] = useUpdateCourseMutation();
  const [createModule] = useCreateModuleMutation();
  const [updateModule] = useUpdateModuleMutation();
  const [deleteModule] = useDeleteModuleMutation();

  const [course, setCourse] = useState({
    title: '',
    description: '',
    category: 'General'
  });
  const [courseErrors, setCourseErrors] = useState({
    title: '',
    description: '',
    category: ''
  });
  const [courseTouched, setCourseTouched] = useState({
    title: false,
    description: false,
    category: false
  });
  const [error, setError] = useState('');
  const [showModuleForm, setShowModuleForm] = useState(false);
  const [editingModule, setEditingModule] = useState(null);
  const [moduleForm, setModuleForm] = useState({
    title: '',
    description: '',
    order: 1
  });
  const [moduleErrors, setModuleErrors] = useState({
    title: '',
    description: '',
    order: ''
  });
  const [moduleTouched, setModuleTouched] = useState({
    title: false,
    description: false,
    order: false
  });
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [moduleToDelete, setModuleToDelete] = useState(null);

  const originalCourse = useMemo(() => {
    if (courseData?.course) {
      return {
        title: courseData.course.title || '',
        description: courseData.course.description || '',
        category: courseData.course.category || 'General'
      };
    }
    return null;
  }, [courseData]);

  React.useEffect(() => {
    if (courseData?.course) {
      setCourse({
        title: courseData.course.title || '',
        description: courseData.course.description || '',
        category: courseData.course.category || 'General'
      });
    }
  }, [courseData]);

  useEffect(() => {
    if (showModuleForm && editingModule && moduleFormRef.current) {
      setTimeout(() => {
        moduleFormRef.current.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
          inline: 'nearest'
        });
      }, 100);
    }
  }, [showModuleForm, editingModule]);


  const hasChanges = useMemo(() => {
    if (isNew || !originalCourse) return true;
    return (
      course.title !== originalCourse.title ||
      course.description !== originalCourse.description ||
      course.category !== originalCourse.category
    );
  }, [course, originalCourse, isNew]);

  const modules = modulesData?.modules || [];

  const handleCourseChange = (field, value) => {
    setCourse(prev => ({ ...prev, [field]: value }));


    if (courseTouched[field]) {
      validateCourseField(field, value);
    }
  };

  const validateCourseField = (field, value) => {
    let validation;

    switch (field) {
      case 'title':
        validation = validateTitle(value, { fieldName: 'Course title' });
        setCourseErrors(prev => ({ ...prev, title: validation.error }));
        if (validation.isValid && validation.value) {
          setCourse(prev => ({ ...prev, title: validation.value }));
        }
        break;
      case 'description':
        validation = validateDescription(value, { fieldName: 'Description' });
        setCourseErrors(prev => ({ ...prev, description: validation.error }));
        if (validation.isValid && validation.value) {
          setCourse(prev => ({ ...prev, description: validation.value }));
        }
        break;
      case 'category':
        validation = validateCategory(value);
        setCourseErrors(prev => ({ ...prev, category: validation.error }));
        if (validation.isValid && validation.value !== undefined) {
          setCourse(prev => ({ ...prev, category: validation.value }));
        }
        break;
      default:
        break;
    }
  };

  const handleCourseBlur = (field, value) => {
    setCourseTouched(prev => ({ ...prev, [field]: true }));
    validateCourseField(field, value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');


    const allTouched = {
      title: true,
      description: true,
      category: true
    };
    setCourseTouched(allTouched);


    const titleValidation = validateTitle(course.title, { fieldName: 'Course title' });
    const descriptionValidation = validateDescription(course.description, { fieldName: 'Description' });
    const categoryValidation = validateCategory(course.category);

    const newErrors = {
      title: titleValidation.error,
      description: descriptionValidation.error,
      category: categoryValidation.error
    };

    setCourseErrors(newErrors);

    if (!titleValidation.isValid || !descriptionValidation.isValid || !categoryValidation.isValid) {
      return;
    }

    try {
      const courseData = {
        title: titleValidation.value || course.title.trim(),
        description: descriptionValidation.value || course.description.trim(),
        category: categoryValidation.value !== undefined ? categoryValidation.value : course.category.trim()
      };

      if (isNew) {
        const response = await createCourse(courseData).unwrap();
        navigate(`/instructor/courses/${response.course.courseId}/edit`);
      } else {
        await updateCourse({ id, ...courseData }).unwrap();
        toast.success('Course updated successfully!');
      }
    } catch (err) {
      setError(err.data?.error || 'Failed to save course');
    }
  };

  const handleModuleChange = (field, value) => {
    if (field === 'order') {
      setModuleForm(prev => ({ ...prev, [field]: parseInt(value) || 1 }));
    } else {
      setModuleForm(prev => ({ ...prev, [field]: value }));
    }


    if (moduleTouched[field]) {
      validateModuleField(field, field === 'order' ? parseInt(value) || 1 : value);
    }
  };

  const validateModuleField = (field, value) => {
    let validation;

    switch (field) {
      case 'title':
        validation = validateTitle(value, { fieldName: 'Module title' });
        setModuleErrors(prev => ({ ...prev, title: validation.error }));
        if (validation.isValid && validation.value) {
          setModuleForm(prev => ({ ...prev, title: validation.value }));
        }
        break;
      case 'description':
        validation = validateModuleDescription(value);
        setModuleErrors(prev => ({ ...prev, description: validation.error }));
        if (validation.isValid && validation.value) {
          setModuleForm(prev => ({ ...prev, description: validation.value }));
        }
        break;
      case 'order':
        validation = validateNumber(value, { fieldName: 'Order', min: 1, max: 999 });
        setModuleErrors(prev => ({ ...prev, order: validation.error }));
        if (validation.isValid && validation.value !== null) {
          setModuleForm(prev => ({ ...prev, order: validation.value }));
        }
        break;
      default:
        break;
    }
  };

  const handleModuleBlur = (field, value) => {
    setModuleTouched(prev => ({ ...prev, [field]: true }));
    validateModuleField(field, field === 'order' ? parseInt(value) || 1 : value);
  };

  const handleAddModule = async (e) => {
    e.preventDefault();


    const allTouched = {
      title: true,
      description: true,
      order: true
    };
    setModuleTouched(allTouched);


    const titleValidation = validateTitle(moduleForm.title, { fieldName: 'Module title' });
    const descriptionValidation = validateModuleDescription(moduleForm.description);
    const orderValidation = validateNumber(moduleForm.order, { fieldName: 'Order', min: 1, max: 999 });

    const newErrors = {
      title: titleValidation.error,
      description: descriptionValidation.error,
      order: orderValidation.error
    };

    setModuleErrors(newErrors);

    if (!titleValidation.isValid || !descriptionValidation.isValid || !orderValidation.isValid) {
      return;
    }

    try {
      const order = orderValidation.value || moduleForm.order;
      const moduleData = {
        title: titleValidation.value || moduleForm.title.trim(),
        description: descriptionValidation.value || moduleForm.description.trim(),
        order: order
      };

      if (editingModule) {
        await updateModule({
          id: editingModule.moduleId,
          courseId: id,
          ...moduleData
        }).unwrap();
        toast.success('Module updated successfully!');
      } else {
        await createModule({
          courseId: id,
          ...moduleData
        }).unwrap();
        toast.success('Module created successfully!');
      }
      setShowModuleForm(false);
      setEditingModule(null);
      setModuleForm({ title: '', description: '', order: modules.length + 1 });
      setModuleErrors({ title: '', description: '', order: '' });
      setModuleTouched({ title: false, description: false, order: false });
      refetchModules();
    } catch (err) {
      toast.error(err.data?.error || 'Failed to save module');
    }
  };

  const handleEditModule = (module) => {
    setEditingModule(module);
    setModuleForm({
      title: module.title,
      description: module.description,
      order: module.order || modules.length + 1
    });
    setModuleErrors({ title: '', description: '', order: '' });
    setModuleTouched({ title: false, description: false, order: false });
    setShowModuleForm(true);

    setTimeout(() => {
      if (moduleFormRef.current) {
        moduleFormRef.current.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    }, 100);
  };

  const handleDeleteModuleClick = (moduleId) => {
    setModuleToDelete(moduleId);
    setShowDeleteModal(true);
  };

  const handleDeleteModule = async () => {
    if (!moduleToDelete) return;

    try {
      await deleteModule({ id: moduleToDelete, courseId: id }).unwrap();
      toast.success('Module deleted successfully!');
      refetchModules();
      setModuleToDelete(null);
    } catch (err) {
      toast.error(err.data?.error || 'Failed to delete module');
    }
  };

  const handleCancelModuleForm = () => {
    setShowModuleForm(false);
    setEditingModule(null);
    setModuleForm({ title: '', description: '', order: modules.length + 1 });
    setModuleErrors({ title: '', description: '', order: '' });
    setModuleTouched({ title: false, description: false, order: false });
  };

  if (courseLoading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <button
          onClick={() => navigate(-1)}
          className="back-button"
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: '#3498db',
            fontSize: '1.2rem',
            padding: '0',
            margin: '0',
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <span>←</span>
        </button>
        {isNew ? 'Create New Course' : 'Edit Course'}
      </h1>
      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit} className="card" style={{ marginTop: '1rem' }}>
        <div className="form-group">
          <label>Course Title *</label>
          <input
            type="text"
            value={course.title}
            onChange={(e) => handleCourseChange('title', e.target.value)}
            onBlur={(e) => handleCourseBlur('title', e.target.value)}
            className={courseTouched.title && courseErrors.title ? 'input-error' : ''}
            required
          />
          {courseTouched.title && courseErrors.title && (
            <span className="error-message">{courseErrors.title}</span>
          )}
        </div>
        <div className="form-group">
          <label>Description *</label>
          <textarea
            value={course.description}
            onChange={(e) => handleCourseChange('description', e.target.value)}
            onBlur={(e) => handleCourseBlur('description', e.target.value)}
            className={courseTouched.description && courseErrors.description ? 'input-error' : ''}
            required
            rows="5"
          />
          {courseTouched.description && courseErrors.description && (
            <span className="error-message">{courseErrors.description}</span>
          )}
        </div>
        <div className="form-group">
          <label>Category</label>
          <input
            type="text"
            value={course.category}
            onChange={(e) => handleCourseChange('category', e.target.value)}
            onBlur={(e) => handleCourseBlur('category', e.target.value)}
            className={courseTouched.category && courseErrors.category ? 'input-error' : ''}
          />
          {courseTouched.category && courseErrors.category && (
            <span className="error-message">{courseErrors.category}</span>
          )}
          <small style={{ color: '#666' }}>Optional - e.g., &quot;General&quot;, &quot;Advanced&quot;, etc.</small>
        </div>
        <button type="submit" className="btn btn-primary" disabled={!isNew && !hasChanges}>
          {isNew ? 'Create Course' : 'Update Course'}
        </button>
      </form>

      {!isNew && (
        <div style={{ marginTop: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2>Modules ({modules.length})</h2>
            {!showModuleForm && (
              <button
                onClick={() => {
                  setModuleForm({ title: '', description: '', order: modules.length + 1 });
                  setShowModuleForm(true);
                  setEditingModule(null);
                }}
                className="btn btn-primary"
              >
                Add Module
              </button>
            )}
          </div>

          {showModuleForm && (
            <div ref={moduleFormRef} className="card" style={{ marginBottom: '2rem' }}>
              <h3>{editingModule ? 'Edit Module' : 'Add New Module'}</h3>
              <form onSubmit={handleAddModule}>
                <div className="form-group">
                  <label>Module Title *</label>
                  <input
                    type="text"
                    value={moduleForm.title}
                    onChange={(e) => handleModuleChange('title', e.target.value)}
                    onBlur={(e) => handleModuleBlur('title', e.target.value)}
                    className={moduleTouched.title && moduleErrors.title ? 'input-error' : ''}
                    required
                  />
                  {moduleTouched.title && moduleErrors.title && (
                    <span className="error-message">{moduleErrors.title}</span>
                  )}
                </div>
                <div className="form-group">
                  <label>Description *</label>
                  <textarea
                    value={moduleForm.description}
                    onChange={(e) => handleModuleChange('description', e.target.value)}
                    onBlur={(e) => handleModuleBlur('description', e.target.value)}
                    className={moduleTouched.description && moduleErrors.description ? 'input-error' : ''}
                    required
                    rows="4"
                  />
                  {moduleTouched.description && moduleErrors.description && (
                    <span className="error-message">{moduleErrors.description}</span>
                  )}
                </div>
                <div className="form-group">
                  <label>Order</label>
                  <input
                    type="number"
                    value={moduleForm.order}
                    onChange={(e) => handleModuleChange('order', e.target.value)}
                    onBlur={(e) => handleModuleBlur('order', e.target.value)}
                    className={moduleTouched.order && moduleErrors.order ? 'input-error' : ''}
                    min="1"
                    max="999"
                  />
                  {moduleTouched.order && moduleErrors.order && (
                    <span className="error-message">{moduleErrors.order}</span>
                  )}
                  {!moduleTouched.order && (
                    <small style={{ color: '#666' }}>Modules are displayed in this order (1-999)</small>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button type="submit" className="btn btn-primary">
                    {editingModule ? 'Update Module' : 'Create Module'}
                  </button>
                  <button type="button" onClick={handleCancelModuleForm} className="btn btn-secondary">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {modules.length === 0 ? (
            <div className="card">
              <p>No modules yet. Add your first module to get started!</p>
            </div>
          ) : (
            <div className="grid grid-2">
              {[...modules]
                .sort((a, b) => (a.order || 0) - (b.order || 0))
                .map((module) => (
                <div key={module.moduleId} className="card">
                  <h3>{module.title}</h3>
                  <p>{module.description}</p>
                  <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
                    Order: {module.order || 'Not set'}
                  </p>
                  <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                    <button
                      onClick={() => handleEditModule(module)}
                      className="btn btn-secondary"
                      style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteModuleClick(module.moduleId)}
                      className="btn btn-danger"
                      style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setModuleToDelete(null);
        }}
        onConfirm={handleDeleteModule}
        title="Delete Module"
        message="Are you sure you want to delete this module? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />
    </div>
  );
};

export default InstructorCourseManage;

