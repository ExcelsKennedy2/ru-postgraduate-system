-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 18, 2026 at 02:15 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `syncpath_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `aitranscript`
--

CREATE TABLE `aitranscript` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `source_file_url` varchar(255) NOT NULL,
  `ai_feedback` text DEFAULT NULL,
  `status` enum('pending','processed','reviewed') DEFAULT 'pending',
  `created_at` datetime DEFAULT current_timestamp(),
  `processed_at` datetime DEFAULT NULL,
  `reviewed_by_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `aitranscript`
--

INSERT INTO `aitranscript` (`id`, `student_id`, `source_file_url`, `ai_feedback`, `status`, `created_at`, `processed_at`, `reviewed_by_id`) VALUES
(5, 1, '/files/alice_transcript.pdf', 'Looks good', 'processed', '2026-03-18 16:10:45', '2026-03-18 16:10:45', 1),
(6, 2, '/files/bob_transcript.pdf', 'Needs minor edits', 'reviewed', '2026-03-18 16:10:45', '2026-03-18 16:10:45', 2);

-- --------------------------------------------------------

--
-- Table structure for table `assessmentrubric`
--

CREATE TABLE `assessmentrubric` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `rubric_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`rubric_data`)),
  `weighted_score` decimal(5,2) DEFAULT NULL,
  `auto_pass_fail` tinyint(1) DEFAULT NULL,
  `evaluated_by_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `assessmentrubric`
--

INSERT INTO `assessmentrubric` (`id`, `student_id`, `rubric_data`, `weighted_score`, `auto_pass_fail`, `evaluated_by_id`) VALUES
(3, 1, '{\"score\":90}', 90.00, 1, 1),
(4, 2, '{\"score\":75}', 75.00, 1, 2);

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `recipient_id` int(11) NOT NULL,
  `type` enum('pipeline_update','seminar_reminder','ai_feedback','general') NOT NULL,
  `message` text NOT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `read_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `recipient_id`, `type`, `message`, `is_read`, `created_at`, `read_at`) VALUES
(1, 1, 'pipeline_update', 'Your stage has been updated', 0, '2026-03-18 16:12:10', NULL),
(2, 2, 'seminar_reminder', 'Seminar tomorrow at 10AM', 0, '2026-03-18 16:12:10', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `pipeline`
--

CREATE TABLE `pipeline` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `current_stage` enum('applied','in_review','accepted','in_progress','completed') NOT NULL,
  `assigned_mentor_id` int(11) DEFAULT NULL,
  `last_updated` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pipeline`
--

INSERT INTO `pipeline` (`id`, `student_id`, `current_stage`, `assigned_mentor_id`, `last_updated`) VALUES
(1, 1, 'applied', 3, '2026-03-18 15:48:13'),
(2, 2, 'in_review', 3, '2026-03-18 15:48:13'),
(3, 1, 'applied', 1, '2026-03-18 15:59:53'),
(4, 2, 'in_review', 2, '2026-03-18 15:59:53');

-- --------------------------------------------------------

--
-- Table structure for table `pipelinehistory`
--

CREATE TABLE `pipelinehistory` (
  `id` int(11) NOT NULL,
  `pipeline_id` int(11) NOT NULL,
  `previous_stage` enum('applied','in_review','accepted','in_progress','completed') DEFAULT NULL,
  `new_stage` enum('applied','in_review','accepted','in_progress','completed') NOT NULL,
  `changed_by_id` int(11) DEFAULT NULL,
  `changed_at` datetime DEFAULT current_timestamp(),
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pipelinehistory`
--

INSERT INTO `pipelinehistory` (`id`, `pipeline_id`, `previous_stage`, `new_stage`, `changed_by_id`, `changed_at`, `notes`) VALUES
(1, 1, NULL, 'applied', 3, '2026-03-18 15:48:26', 'Initial stage'),
(2, 2, 'applied', 'in_review', 3, '2026-03-18 15:48:26', 'Moved to review');

-- --------------------------------------------------------

--
-- Table structure for table `quarterlyreports`
--

CREATE TABLE `quarterlyreports` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `report_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`report_data`)),
  `signatures` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`signatures`)),
  `created_at` datetime DEFAULT current_timestamp(),
  `approved` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `quarterlyreports`
--

INSERT INTO `quarterlyreports` (`id`, `student_id`, `report_data`, `signatures`, `created_at`, `approved`) VALUES
(1, 1, '{\"progress\":\"good\"}', '{\"signatures\":[]}', '2026-03-18 16:11:50', 1),
(2, 2, '{\"progress\":\"average\"}', '{\"signatures\":[]}', '2026-03-18 16:11:50', 0);

-- --------------------------------------------------------

--
-- Table structure for table `seminarbookings`
--

CREATE TABLE `seminarbookings` (
  `id` int(11) NOT NULL,
  `seminar_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `status` enum('booked','canceled','attended') DEFAULT 'booked',
  `booking_time` datetime DEFAULT current_timestamp(),
  `cancellation_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `seminarbookings`
--

INSERT INTO `seminarbookings` (`id`, `seminar_id`, `student_id`, `status`, `booking_time`, `cancellation_time`) VALUES
(5, 11, 1, 'booked', '2026-03-18 16:07:01', NULL),
(6, 12, 2, 'booked', '2026-03-18 16:07:01', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `seminars`
--

CREATE TABLE `seminars` (
  `id` int(11) NOT NULL,
  `title` varchar(150) NOT NULL,
  `description` text DEFAULT NULL,
  `instructor_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `time` time NOT NULL,
  `location` varchar(150) DEFAULT NULL,
  `max_attendees` int(11) DEFAULT 30
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `seminars`
--

INSERT INTO `seminars` (`id`, `title`, `description`, `instructor_id`, `date`, `time`, `location`, `max_attendees`) VALUES
(11, 'AI Techniques', 'Intro to AI', 3, '2026-03-18', '10:00:00', 'Room 101', 20),
(12, 'Data Science', 'Deep Dive', 3, '2026-03-18', '14:00:00', 'Room 102', 25);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('student','mentor','chair','admin','dean') NOT NULL,
  `date_joined` datetime DEFAULT current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `first_name`, `last_name`, `email`, `password_hash`, `role`, `date_joined`, `is_active`) VALUES
(1, 'Alice', 'Wong', 'alice@example.com', 'hashedPassword1', 'student', '2026-03-18 15:46:37', 1),
(2, 'Bob', 'Kim', 'bob@example.com', 'hashedPassword2', 'student', '2026-03-18 15:46:37', 1),
(3, 'John', 'Doe', 'john@example.com', 'hashedPassword3', 'mentor', '2026-03-18 15:46:37', 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `aitranscript`
--
ALTER TABLE `aitranscript`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_transcript_student` (`student_id`),
  ADD KEY `fk_transcript_reviewer` (`reviewed_by_id`);

--
-- Indexes for table `assessmentrubric`
--
ALTER TABLE `assessmentrubric`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_rubric_student` (`student_id`),
  ADD KEY `fk_rubric_evaluator` (`evaluated_by_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_notification_recipient` (`recipient_id`);

--
-- Indexes for table `pipeline`
--
ALTER TABLE `pipeline`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_pipeline_student` (`student_id`),
  ADD KEY `fk_pipeline_mentor` (`assigned_mentor_id`);

--
-- Indexes for table `pipelinehistory`
--
ALTER TABLE `pipelinehistory`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_history_pipeline` (`pipeline_id`),
  ADD KEY `fk_history_user` (`changed_by_id`);

--
-- Indexes for table `quarterlyreports`
--
ALTER TABLE `quarterlyreports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_report_student` (`student_id`);

--
-- Indexes for table `seminarbookings`
--
ALTER TABLE `seminarbookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_booking_seminar` (`seminar_id`),
  ADD KEY `fk_booking_student` (`student_id`);

--
-- Indexes for table `seminars`
--
ALTER TABLE `seminars`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_seminar_instructor` (`instructor_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `aitranscript`
--
ALTER TABLE `aitranscript`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `assessmentrubric`
--
ALTER TABLE `assessmentrubric`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `pipeline`
--
ALTER TABLE `pipeline`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `pipelinehistory`
--
ALTER TABLE `pipelinehistory`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `quarterlyreports`
--
ALTER TABLE `quarterlyreports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `seminarbookings`
--
ALTER TABLE `seminarbookings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `seminars`
--
ALTER TABLE `seminars`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `aitranscript`
--
ALTER TABLE `aitranscript`
  ADD CONSTRAINT `fk_transcript_reviewer` FOREIGN KEY (`reviewed_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_transcript_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `assessmentrubric`
--
ALTER TABLE `assessmentrubric`
  ADD CONSTRAINT `fk_rubric_evaluator` FOREIGN KEY (`evaluated_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_rubric_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `fk_notification_recipient` FOREIGN KEY (`recipient_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `pipeline`
--
ALTER TABLE `pipeline`
  ADD CONSTRAINT `fk_pipeline_mentor` FOREIGN KEY (`assigned_mentor_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_pipeline_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `pipelinehistory`
--
ALTER TABLE `pipelinehistory`
  ADD CONSTRAINT `fk_history_pipeline` FOREIGN KEY (`pipeline_id`) REFERENCES `pipeline` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_history_user` FOREIGN KEY (`changed_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `quarterlyreports`
--
ALTER TABLE `quarterlyreports`
  ADD CONSTRAINT `fk_report_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `seminarbookings`
--
ALTER TABLE `seminarbookings`
  ADD CONSTRAINT `fk_booking_seminar` FOREIGN KEY (`seminar_id`) REFERENCES `seminars` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_booking_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `seminars`
--
ALTER TABLE `seminars`
  ADD CONSTRAINT `fk_seminar_instructor` FOREIGN KEY (`instructor_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
