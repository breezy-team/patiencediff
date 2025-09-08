use pyo3::prelude::*;
use pyo3::types::{PyList, PySequence, PyTuple};

/// Find the longest common subsequence of unique elements in sequences a and b.
///
/// Returns a list of (i, j) tuples where a[i] == b[j].
/// This implementation uses the patience sorting algorithm.
#[pyfunction]
fn unique_lcs_rs<'py>(
    py: Python<'py>,
    a: Bound<'py, PyAny>,
    b: Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyList>> {
    // Convert Python sequences to vectors of PyItem for patiencediff crate
    let a_seq = a.clone();
    let b_seq = b.clone();

    let a_len = a_seq.len()?;
    let b_len = b_seq.len()?;

    // Create PyItem sequences
    let mut a_items = Vec::with_capacity(a_len);
    let mut b_items = Vec::with_capacity(b_len);

    // Extract items from sequences
    for i in 0..a_len {
        let item = a_seq.get_item(i)?;
        a_items.push(PyItem(item.into()));
    }

    for i in 0..b_len {
        let item = b_seq.get_item(i)?;
        b_items.push(PyItem(item.into()));
    }

    // Use patiencediff crate's unique_lcs function
    let matches = patiencediff::unique_lcs(&a_items, &b_items);

    // Create result list
    let result = PyList::empty(py);

    // Add matches to the result list
    for &(a_pos, b_pos) in &matches {
        let tuple = PyTuple::new(py, &[a_pos, b_pos])?;
        result.append(tuple)?;
    }

    Ok(result)
}

/// Python item wrapper that implements the necessary traits for patiencediff crate
struct PyItem(PyObject);

// Implement Clone for PyItem using clone_ref() for PyObject
impl Clone for PyItem {
    fn clone(&self) -> Self {
        Python::with_gil(|py| PyItem(self.0.clone_ref(py)))
    }
}

// Define equality for PyItem that uses Python's eq
impl PartialEq for PyItem {
    fn eq(&self, other: &Self) -> bool {
        Python::with_gil(|py| {
            let a = self.0.extract::<Bound<PyAny>>(py).unwrap();
            let b = other.0.extract::<Bound<PyAny>>(py).unwrap();
            a.eq(&b).unwrap_or(false)
        })
    }
}

impl Eq for PyItem {}

// Define hashing for PyItem that uses Python's hash
impl std::hash::Hash for PyItem {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        let hash_value = Python::with_gil(|py| {
            let obj = self.0.extract::<Bound<PyAny>>(py).unwrap();
            match obj.hash() {
                Ok(hash) => hash,
                Err(e) => {
                    // Properly propagate a TypeError without panicking
                    if e.is_instance_of::<pyo3::exceptions::PyTypeError>(py) {
                        return 0; // Use a constant hash for unhashable types
                    }
                    // For any other errors, use a different constant
                    return 1;
                }
            }
        });
        state.write_isize(hash_value);
    }
}

/// Recursively find matches between two sequences.
///
/// This function wraps the patiencediff crate's recurse_matches function.
#[pyfunction]
fn recurse_matches_rs<'py>(
    py: Python<'py>,
    a: Bound<'py, PyAny>,
    b: Bound<'py, PyAny>,
    alo: usize,
    blo: usize,
    ahi: usize,
    bhi: usize,
    answer: Bound<'py, PyList>,
    maxrecursion: i32,
) -> PyResult<()> {
    // Early return for base cases
    if maxrecursion < 0 || alo == ahi || blo == bhi {
        return Ok(());
    }

    // Convert Python sequences to vectors of PyItem for patiencediff crate
    let a_seq = a.clone();
    let b_seq = b.clone();

    // Create vectors of PyItems for the sliced sequences
    let mut a_items = Vec::with_capacity(ahi - alo);
    let mut b_items = Vec::with_capacity(bhi - blo);

    // Extract the items we need from the sequences
    for i in alo..ahi {
        let item = a_seq.get_item(i)?;
        a_items.push(PyItem(item.into()));
    }

    for i in blo..bhi {
        let item = b_seq.get_item(i)?;
        b_items.push(PyItem(item.into()));
    }

    // Create a vector to collect the matches
    let mut matches = Vec::new();

    // Call the patiencediff crate's recurse_matches function
    patiencediff::recurse_matches(
        &a_items,
        &b_items,
        0,
        0,
        a_items.len(),
        b_items.len(),
        &mut matches,
        maxrecursion,
    );

    // Convert the results to Python and add to the answer list
    for &(rel_a, rel_b) in &matches {
        let a_pos = rel_a + alo;
        let b_pos = rel_b + blo;

        let tuple = PyTuple::new(py, &[a_pos, b_pos])?;
        answer.append(tuple)?;
    }

    Ok(())
}

/// The PatienceSequenceMatcher class
#[pyclass(name = "PatienceSequenceMatcher_rs")]
struct PatienceSequenceMatcherRs {
    matcher: patiencediff::SequenceMatcher<PyItem>,
}

#[pymethods]
impl PatienceSequenceMatcherRs {
    #[new]
    fn new(py: Python<'_>, _junk: Option<PyObject>, a: PyObject, b: PyObject) -> PyResult<Self> {
        // Extract sequences
        let a_any = a.extract::<Bound<PyAny>>(py)?;
        let b_any = b.extract::<Bound<PyAny>>(py)?;

        // Convert to sequences
        let a_seq = a_any.downcast::<PySequence>()?;
        let b_seq = b_any.downcast::<PySequence>()?;

        let a_len = a_seq.len()?;
        let b_len = b_seq.len()?;

        // Create PyItem sequences
        let mut a_items = Vec::with_capacity(a_len);
        let mut b_items = Vec::with_capacity(b_len);

        // Check if all items are hashable before proceeding
        for i in 0..a_len {
            let item = a_seq.get_item(i)?;
            // Try to hash the item to check if it's hashable
            if let Err(e) = item.hash() {
                if e.is_instance_of::<pyo3::exceptions::PyTypeError>(py) {
                    return Err(pyo3::exceptions::PyTypeError::new_err("unhashable type"));
                }
                return Err(e);
            }
            a_items.push(PyItem(item.into()));
        }

        for i in 0..b_len {
            let item = b_seq.get_item(i)?;
            // Try to hash the item to check if it's hashable
            if let Err(e) = item.hash() {
                if e.is_instance_of::<pyo3::exceptions::PyTypeError>(py) {
                    return Err(pyo3::exceptions::PyTypeError::new_err("unhashable type"));
                }
                return Err(e);
            }
            b_items.push(PyItem(item.into()));
        }

        // Create and return the matcher
        let matcher = patiencediff::SequenceMatcher::new(&a_items, &b_items);

        Ok(Self { matcher })
    }

    /// Return list of triples describing matching subsequences.
    ///
    /// Each triple is of the form (i, j, n), and means that
    /// a[i:i+n] == b[j:j+n].  The triples are monotonically increasing in
    /// i and in j.
    ///
    /// The last triple is a dummy, (len(a), len(b), 0), and is the only
    /// triple with n==0.
    fn get_matching_blocks<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        // Get matching blocks from the matcher
        let blocks = self.matcher.get_matching_blocks();

        // Import difflib.Match
        let difflib = py.import("difflib")?;
        let match_class = difflib.getattr("Match")?;

        // Convert blocks to Python list
        let result = PyList::empty(py);

        for &(a, b, size) in blocks {
            // Create a Match named tuple instead of a regular tuple
            let match_obj = match_class.call1((a, b, size))?;
            result.append(match_obj)?;
        }

        Ok(result)
    }

    /// Return list of 5-tuples describing how to turn a into b.
    ///
    /// Each tuple is of the form (tag, i1, i2, j1, j2).  The first tuple
    /// has i1 == j1 == 0, and remaining tuples have i1 == the i2 from the
    /// tuple preceding it, and likewise for j1 == the previous j2.
    ///
    /// The tags are strings, with these meanings:
    ///
    /// 'replace':  a[i1:i2] should be replaced by b[j1:j2]
    /// 'delete':   a[i1:i2] should be deleted.
    ///                Note that j1==j2 in this case.
    /// 'insert':   b[j1:j2] should be inserted at a[i1:i1].
    ///                Note that i1==i2 in this case.
    /// 'equal':    a[i1:i2] == b[j1:j2]
    fn get_opcodes<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        // Get opcodes directly from the matcher
        let opcodes = self.matcher.get_opcodes();

        // Convert opcodes to Python list
        let result = PyList::empty(py);

        for opcode in opcodes {
            match opcode {
                patiencediff::Opcode::Equal(i1, i2, j1, j2) => {
                    let tuple = PyTuple::new(
                        py,
                        &[
                            "equal".into_pyobject(py)?.into_any().unbind(),
                            i1.into_pyobject(py)?.into_any().unbind(),
                            i2.into_pyobject(py)?.into_any().unbind(),
                            j1.into_pyobject(py)?.into_any().unbind(),
                            j2.into_pyobject(py)?.into_any().unbind(),
                        ],
                    )?;
                    result.append(tuple)?;
                }
                patiencediff::Opcode::Replace(i1, i2, j1, j2) => {
                    let tuple = PyTuple::new(
                        py,
                        &[
                            "replace".into_pyobject(py)?.into_any().unbind(),
                            i1.into_pyobject(py)?.into_any().unbind(),
                            i2.into_pyobject(py)?.into_any().unbind(),
                            j1.into_pyobject(py)?.into_any().unbind(),
                            j2.into_pyobject(py)?.into_any().unbind(),
                        ],
                    )?;
                    result.append(tuple)?;
                }
                patiencediff::Opcode::Delete(i1, i2, j1, j2) => {
                    let tuple = PyTuple::new(
                        py,
                        &[
                            "delete".into_pyobject(py)?.into_any().unbind(),
                            i1.into_pyobject(py)?.into_any().unbind(),
                            i2.into_pyobject(py)?.into_any().unbind(),
                            j1.into_pyobject(py)?.into_any().unbind(),
                            j2.into_pyobject(py)?.into_any().unbind(),
                        ],
                    )?;
                    result.append(tuple)?;
                }
                patiencediff::Opcode::Insert(i1, i2, j1, j2) => {
                    let tuple = PyTuple::new(
                        py,
                        &[
                            "insert".into_pyobject(py)?.into_any().unbind(),
                            i1.into_pyobject(py)?.into_any().unbind(),
                            i2.into_pyobject(py)?.into_any().unbind(),
                            j1.into_pyobject(py)?.into_any().unbind(),
                            j2.into_pyobject(py)?.into_any().unbind(),
                        ],
                    )?;
                    result.append(tuple)?;
                }
            }
        }

        Ok(result)
    }

    /// Return a list of groups with upto n lines of context.
    ///
    /// Each group is in the same format as returned by get_opcodes().
    fn get_grouped_opcodes<'py>(
        &mut self,
        py: Python<'py>,
        n: Option<usize>,
    ) -> PyResult<Bound<'py, PyList>> {
        let n = n.unwrap_or(3);

        // Get grouped opcodes directly from the matcher
        let grouped_opcodes = self.matcher.get_grouped_opcodes(n);

        // Convert to Python list
        let result = PyList::empty(py);

        for group in grouped_opcodes {
            let group_list = PyList::empty(py);

            for opcode in group {
                let (tag, i1, i2, j1, j2) = match opcode {
                    patiencediff::Opcode::Equal(i1, i2, j1, j2) => ("equal", i1, i2, j1, j2),
                    patiencediff::Opcode::Replace(i1, i2, j1, j2) => ("replace", i1, i2, j1, j2),
                    patiencediff::Opcode::Delete(i1, i2, j1, j2) => ("delete", i1, i2, j1, j2),
                    patiencediff::Opcode::Insert(i1, i2, j1, j2) => ("insert", i1, i2, j1, j2),
                };

                let tuple = PyTuple::new(
                    py,
                    &[
                        tag.into_pyobject(py)?.into_any().unbind(),
                        i1.into_pyobject(py)?.into_any().unbind(),
                        i2.into_pyobject(py)?.into_any().unbind(),
                        j1.into_pyobject(py)?.into_any().unbind(),
                        j2.into_pyobject(py)?.into_any().unbind(),
                    ],
                )?;

                group_list.append(tuple)?;
            }

            if group_list.len() > 0 {
                result.append(group_list)?;
            }
        }

        // Note: We're not adding a default group for empty result anymore
        Ok(result)
    }
}

#[pymodule]
fn _patiencediff_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PatienceSequenceMatcherRs>()?;
    m.add_function(wrap_pyfunction!(unique_lcs_rs, m)?)?;
    m.add_function(wrap_pyfunction!(recurse_matches_rs, m)?)?;
    Ok(())
}
